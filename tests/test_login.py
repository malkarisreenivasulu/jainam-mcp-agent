from unittest.mock import Mock

import pytest

from jainam_mcp import login
from jainam_mcp.config import ConfigError


@pytest.mark.parametrize("target", ["/favicon.ico", "/callback", "/callback?userId=u&authCode=",
                                    "/callback?userId=u&authCode=a&authCode=b",
                                    "/callback?userId=u&authCode=%0Acode"])
def test_invalid_callback(target):
    assert login.callback_values(target) is None


def test_callback_decodes_values():
    assert login.callback_values("/callback?userId=test%20user&authCode=a%2Bb") == ("test user", "a+b")


def test_bind_failure_does_not_open_browser(monkeypatch):
    import socket

    browser = Mock()
    monkeypatch.setattr(login.webbrowser, "open", browser)
    with socket.socket() as occupied:
        occupied.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        occupied.bind(("127.0.0.1", 8765))
        occupied.listen()
        with pytest.raises(ConfigError, match="port 8765"):
            login.capture_callback("https://example.com")
    browser.assert_not_called()


def test_timeout_closes_listener(monkeypatch):
    monkeypatch.setattr(login.webbrowser, "open", lambda url: True)
    with pytest.raises(ConfigError, match="timed out"):
        login.capture_callback("https://example.com", timeout=0)
    # A second bind succeeds: timeout released the previous listener.
    with pytest.raises(ConfigError, match="timed out"):
        login.capture_callback("https://example.com", timeout=0)


def test_real_loopback_capture_rejects_noise_and_hides_query(monkeypatch, capsys):
    import threading
    import urllib.error
    import urllib.request

    threads = []
    failures = []

    def browser(url):
        def visit():
            try:
                try:
                    urllib.request.urlopen("http://127.0.0.1:8765/favicon.ico", timeout=3)
                except urllib.error.HTTPError as exc:
                    assert exc.code == 400
                with urllib.request.urlopen(
                    "http://127.0.0.1:8765/callback?userId=synthetic-user&authCode=synthetic-code",
                    timeout=3,
                ) as response:
                    assert response.status == 200
                    assert response.headers["Cache-Control"] == "no-store"
                    assert b"synthetic-code" not in response.read()
            except Exception as exc:
                failures.append(exc)
        thread = threading.Thread(target=visit)
        threads.append(thread)
        thread.start()
        return True

    monkeypatch.setattr(login.webbrowser, "open", browser)
    assert login.capture_callback("https://example.com", timeout=5) == ("synthetic-user", "synthetic-code")
    for thread in threads:
        thread.join(timeout=5)
        assert not thread.is_alive()
    assert not failures
    output = capsys.readouterr()
    assert "synthetic-code" not in output.out + output.err
