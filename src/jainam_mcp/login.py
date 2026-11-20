"""Bounded loopback callback capture. Broker secrets never enter request logs."""

import os
import socket
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit

from jainam_mcp.config import ConfigError

CALLBACK = "http://127.0.0.1:8765/callback"


def callback_values(target):
    parsed = urlsplit(target)
    if parsed.path != "/callback":
        return None
    query = parse_qs(parsed.query, keep_blank_values=True)
    values = []
    for name in ("userId", "authCode"):
        candidates = query.get(name, [])
        if len(candidates) != 1 or not candidates[0].strip():
            return None
        value = candidates[0]
        if len(value) > 4096 or any(ord(c) < 32 or ord(c) == 127 for c in value):
            return None
        values.append(value)
    return tuple(values)


class CallbackServer(HTTPServer):
    # Windows SO_REUSEADDR permits a second listener on an occupied port.
    allow_reuse_address = os.name != "nt"

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(2)
        return connection, address


def capture_callback(login_url, timeout=180):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            values = callback_values(self.path)
            valid_host = self.headers.get("Host") == "127.0.0.1:8765"
            if values and valid_host:
                self.server.result = values
            self.send_response(200 if values and valid_host else 400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(b"Return to Terminal to finish login. You may close this tab."
                             if values and valid_host else b"Invalid callback. Continue Jainam sign-in.")

    try:
        server = CallbackServer(("127.0.0.1", 8765), Handler)
    except OSError as exc:
        raise ConfigError("Cannot bind local port 8765. Close its other app or use login --manual.") from exc
    with server:
        server.result = None
        server.timeout = 1
        if not webbrowser.open(login_url):
            raise ConfigError("Browser could not open. Use login --manual with your registered callback.")
        deadline = time.monotonic() + timeout
        while server.result is None and time.monotonic() < deadline:
            server.handle_request()
        if server.result is None:
            raise ConfigError("Login timed out. Register the exact redirect URL shown, then retry login.")
        return server.result
