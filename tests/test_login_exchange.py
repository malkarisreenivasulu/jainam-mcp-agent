import hashlib
import json

import pytest
import requests
from jainam_api import Client

from jainam_mcp import cli
from jainam_mcp.config import ConfigError, Credentials, load, save


@pytest.mark.parametrize("status", ["NotOk", "Not_Ok", "Not OK", "ERROR", "Failed"])
def test_broker_rejection_is_not_missing_session(status):
    with pytest.raises(ConfigError, match="AUTH_EXCHANGE_REJECTED") as error:
        cli.extract_session({"status": status, "message": "synthetic-secret", "result": []})
    assert "synthetic-secret" not in str(error.value)


def test_rejected_response_cannot_smuggle_session():
    with pytest.raises(ConfigError, match="AUTH_EXCHANGE_REJECTED"):
        cli.extract_session({"status": "NotOk", "result": [{"userSession": "synthetic-session"}]})


def test_unrecognized_response_diagnostic_contains_no_values_or_arbitrary_keys():
    payload = {"result": [{"token": "synthetic-token", "synthetic-private-key": "private"}],
               "message": "synthetic-secret", "status": "synthetic-status"}
    with pytest.raises(ConfigError, match="AUTH_RESPONSE_UNSUPPORTED") as error:
        cli.extract_session(payload)
    assert '"token":"str"' in str(error.value)
    assert "synthetic" not in str(error.value)
    assert "private" not in str(error.value)


@pytest.mark.parametrize("http_status,payload,expected", [
    (200, {"status": "NotOk", "message": "synthetic-secret", "result": []}, "AUTH_EXCHANGE_REJECTED"),
    (403, {"message": "synthetic-secret"}, "AUTH_HTTP_ERROR"),
    (302, {}, "AUTH_HTTP_ERROR"),
    (200, None, "AUTH_NON_JSON"),
    (200, {"status": "Ok", "result": [{"userSession": "synthetic-session"}]}, None),
])
def test_actual_sdk_exchange_wire_contract(monkeypatch, http_status, payload, expected):
    captured = []

    def send(transport, request, **kwargs):
        captured.append(request)
        assert kwargs["allow_redirects"] is False
        response = requests.Response()
        response.status_code = http_status
        response._content = (
            b"<html>synthetic-secret</html>" if payload is None else json.dumps(payload).encode()
        )
        response._content_consumed = True
        return response

    monkeypatch.setattr(requests.Session, "send", send)
    with cli.LoginSession() as transport:
        client = Client(session=transport)
        if expected:
            with pytest.raises(ConfigError, match=expected) as error:
                client.exchange_auth_code("synthetic-user", "synthetic-code", "synthetic-secret")
            assert "synthetic-secret" not in str(error.value)
        else:
            result = client.exchange_auth_code("synthetic-user", "synthetic-code", "synthetic-secret")
            assert cli.extract_session(result) == "synthetic-session"
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "POST"
    assert request.url == "https://protrade.jainam.in/omt/auth/sso/vendor/getUserDetails"
    assert json.loads(request.body) == {
        "checkSum": hashlib.sha256(b"synthetic-usersynthetic-codesynthetic-secret").hexdigest()
    }
    assert request.headers["Content-Type"] == "application/json"
    assert "Authorization" not in request.headers


def test_failed_setup_preserves_previous_credentials(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("JAINAM_USER_ID", raising=False)
    monkeypatch.delenv("JAINAM_USER_SESSION", raising=False)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    answers = iter(["synthetic-app", "synthetic-secret"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda *a: next(answers))
    monkeypatch.setattr(cli, "capture_callback", lambda url: ("synthetic-user", "synthetic-code"))
    from unittest.mock import Mock

    client = Mock()
    client.exchange_auth_code.return_value = {"status": "NotOk", "result": []}
    monkeypatch.setattr(cli, "Client", lambda **kw: client)
    path = tmp_path / "credentials.json"
    save(Credentials("old-user", "old-session"), path)
    original = path.read_bytes()
    assert cli.main(["--config", str(path), "setup"]) == 1
    assert path.read_bytes() == original
    assert load(path).user_id == "old-user"
    assert "AUTH_EXCHANGE_REJECTED" in capsys.readouterr().err
