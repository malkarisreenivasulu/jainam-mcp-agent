import os
import stat
import threading
from unittest.mock import Mock

import pytest

from jainam_mcp import cli
from jainam_mcp.config import (
    AppCredentials,
    ConfigError,
    Credentials,
    app_path,
    load,
    load_app,
    save,
    save_app,
)
from jainam_mcp.connection import Renewal
from jainam_mcp.service import Service


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("JAINAM_USER_ID", raising=False)
    monkeypatch.delenv("JAINAM_USER_SESSION", raising=False)


def test_remembered_app_is_separate_private_and_repr_safe(tmp_path):
    path = tmp_path / "credentials.json"
    app = AppCredentials("synthetic-app", "synthetic-secret")
    save_app(app, path)
    assert load_app(path) == app
    assert "synthetic" not in repr(app)
    assert not path.exists()
    if os.name == "posix":
        assert stat.S_IMODE(app_path(path).stat().st_mode) == 0o600
        app_path(path).chmod(0o644)
        with pytest.raises(ConfigError, match="private"):
            load_app(path)


def test_connect_valid_session_does_not_prompt_or_open_browser(tmp_path, monkeypatch):
    path = tmp_path / "credentials.json"
    save(Credentials("user", "session"), path)
    monkeypatch.setattr(cli.Service, "account", lambda *a: {"ok": True})
    prompt = Mock(side_effect=AssertionError("should not prompt"))
    monkeypatch.setattr(cli.getpass, "getpass", prompt)
    monkeypatch.setattr(cli, "authorize", prompt)
    cli.connect(path)
    prompt.assert_not_called()


@pytest.mark.parametrize("existing", [False, True])
def test_connect_reuses_app_for_missing_or_expired_session(tmp_path, monkeypatch, existing):
    path = tmp_path / "credentials.json"
    app = AppCredentials("synthetic-app", "synthetic-secret")
    save_app(app, path)
    if existing:
        save(Credentials("user", "old"), path)
    monkeypatch.setattr(
        cli.Service, "account", lambda *a: {"ok": False, "error": "SESSION_EXPIRED_OR_DENIED"}
    )
    monkeypatch.setattr(cli.getpass, "getpass", Mock(side_effect=AssertionError("should not prompt")))
    authorize = Mock(return_value=Credentials("user", "new"))
    monkeypatch.setattr(cli, "authorize", authorize)
    cli.connect(path)
    assert load(path).user_session == "new"
    authorize.assert_called_once_with(app, False)


def test_network_failure_does_not_trigger_login(tmp_path, monkeypatch):
    path = tmp_path / "credentials.json"
    save(Credentials("user", "session"), path)
    monkeypatch.setattr(cli.Service, "account", lambda *a: {"ok": False, "error": "NETWORK_ERROR"})
    login = Mock()
    monkeypatch.setattr(cli, "authorize", login)
    with pytest.raises(ConfigError, match="Cannot check"):
        cli.connect(path)
    login.assert_not_called()


@pytest.mark.parametrize("field", ["accessToken", "sessionToken", "userSessionToken"])
def test_alternate_session_field_requires_broker_validation(monkeypatch, field):
    client = Mock()
    client.exchange_auth_code.return_value = {"status": "Ok", "result": [{field: "synthetic-token"}]}
    monkeypatch.setattr(cli, "Client", lambda **kw: client)
    monkeypatch.setattr(cli, "capture_callback", lambda url: ("user", "code"))
    check = Mock(return_value={"ok": True})
    monkeypatch.setattr(cli.Service, "account", check)
    assert cli.authorize(AppCredentials("app", "secret")).user_session == "synthetic-token"
    check.assert_called_once_with("funds")
    check.return_value = {"ok": False, "error": "BROKER_ERROR"}
    with pytest.raises(ConfigError, match="SESSION_NOT_VERIFIED"):
        cli.authorize(AppCredentials("app", "secret"))


def test_renewal_nonblocking_single_attempt_and_next_read_reloads(tmp_path):
    path = tmp_path / "credentials.json"
    save_app(AppCredentials("app", "secret"), path)
    started = threading.Event()
    finish = threading.Event()
    completed = threading.Event()
    calls = []

    def authorize(app):
        calls.append(app)
        started.set()
        assert finish.wait(3)
        return Credentials("user", "new-session")

    renewal = Renewal(path, authorize)
    original_run = renewal._run

    def run(app):
        original_run(app)
        completed.set()

    renewal._run = run
    client = Mock()
    client.funds.return_value = {"status": "Ok", "result": []}
    service = Service(
        None,
        lambda **kw: client,
        credentials_loader=lambda: load(path),
        auth_required=renewal.begin,
        auth_status=renewal.status,
    )
    assert service.account("funds")["login_state"] == "running"
    assert started.wait(3)
    assert service.account("funds")["login_state"] == "running"
    assert len(calls) == 1
    finish.set()
    assert completed.wait(3)
    assert service.account("funds")["ok"] is True
    assert service.credentials.user_session == "new-session"
    assert service.status()["login_state"] == "ready"


def test_failed_renewal_does_not_loop_or_print_secrets(tmp_path, capsys):
    path = tmp_path / "credentials.json"
    save_app(AppCredentials("app", "secret"), path)
    done = threading.Event()
    calls = []

    def authorize(app):
        calls.append(app)
        raise RuntimeError("synthetic-secret")

    renewal = Renewal(path, authorize)
    original_run = renewal._run

    def run(app):
        original_run(app)
        done.set()

    renewal._run = run
    assert renewal.begin()["login_state"] == "running"
    assert done.wait(3)
    assert renewal.begin()["login_state"] == "failed"
    assert len(calls) == 1
    assert not path.exists()
    output = capsys.readouterr()
    assert "synthetic-secret" not in output.out + output.err


def test_notok_account_result_never_becomes_success():
    client = Mock()
    client.funds.return_value = {"status": "NotOk", "message": "Invalid Session", "result": []}
    callback = Mock(return_value={"login_state": "running"})
    service = Service(Credentials("user", "session"), lambda **kw: client, auth_required=callback)
    result = service.account("funds")
    assert result["ok"] is False
    assert result["login_state"] == "running"
    callback.assert_called_once()


def test_replace_app_updates_remembered_keys(tmp_path, monkeypatch):
    path = tmp_path / "credentials.json"
    save_app(AppCredentials("old-app", "old-secret"), path)
    answers = iter(["new-app", "new-secret"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda *a: next(answers))
    monkeypatch.setattr(cli, "authorize", lambda *a: Credentials("user", "new-session"))
    cli.connect(path, replace_app=True)
    assert load_app(path) == AppCredentials("new-app", "new-secret")


def test_missing_app_requires_one_time_local_connect(tmp_path):
    authorize = Mock()
    renewal = Renewal(tmp_path / "credentials.json", authorize)
    assert renewal.begin()["login_state"] == "setup_required"
    authorize.assert_not_called()


def test_diagnostic_shows_credential_field_names_not_values():
    summary = cli.login_response_summary({"result": [{"sUserToken": "synthetic-secret"}]})
    assert "sUserToken" in summary
    assert "synthetic-secret" not in summary


def test_plain_broker_failure_does_not_open_browser():
    client = Mock()
    client.funds.return_value = {"status": "NotOk", "message": "temporarily unavailable"}
    callback = Mock()
    result = Service(Credentials("user", "session"), lambda **kw: client, auth_required=callback).account(
        "funds"
    )
    assert result["error"] == "BROKER_ERROR"
    callback.assert_not_called()


def test_external_callback_does_not_auto_open_local_listener(tmp_path):
    path = tmp_path / "credentials.json"
    save_app(AppCredentials("app", "secret", automatic_login=False), path)
    login = Mock()
    assert Renewal(path, login).begin()["login_state"] == "manual_required"
    login.assert_not_called()


def test_known_prefixed_token_is_verified_before_use(monkeypatch):
    client = Mock()
    client.exchange_auth_code.return_value = {"status": "Ok", "result": [{"sUserToken": "synthetic-token"}]}
    monkeypatch.setattr(cli, "Client", lambda **kw: client)
    monkeypatch.setattr(cli, "capture_callback", lambda url: ("user", "code"))
    monkeypatch.setattr(cli.Service, "account", lambda *a: {"ok": True})
    assert cli.authorize(AppCredentials("app", "secret")).user_session == "synthetic-token"


def test_ambiguous_alternate_tokens_are_not_probed(monkeypatch):
    client = Mock()
    client.exchange_auth_code.return_value = {"result": [{"accessToken": "one", "sessionToken": "two"}]}
    monkeypatch.setattr(cli, "Client", lambda **kw: client)
    monkeypatch.setattr(cli, "capture_callback", lambda url: ("user", "code"))
    read = Mock()
    monkeypatch.setattr(cli.Service, "account", read)
    with pytest.raises(ConfigError, match="AUTH_RESPONSE_UNSUPPORTED"):
        cli.authorize(AppCredentials("app", "secret"))
    read.assert_not_called()


def test_environment_override_does_not_start_ineffective_renewal(tmp_path, monkeypatch):
    path = tmp_path / "credentials.json"
    save_app(AppCredentials("app", "secret"), path)
    monkeypatch.setenv("JAINAM_USER_ID", "user")
    monkeypatch.setenv("JAINAM_USER_SESSION", "old-session")
    login = Mock()
    assert Renewal(path, login).begin()["login_state"] == "environment_override"
    login.assert_not_called()
