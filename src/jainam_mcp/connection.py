"""Human sign-in and nonblocking renewal for a local MCP process."""

import os
import threading

from jainam_mcp.config import ConfigError, load_app, save


class Renewal:
    def __init__(self, path, authorize):
        self.path = path
        self.authorize = authorize
        self.lock = threading.Lock()
        self.state = "idle"

    def status(self):
        with self.lock:
            return {"login_state": self.state}

    def verified(self):
        with self.lock:
            if self.state != "running":
                self.state = "ready"

    def begin(self):
        with self.lock:
            if any(name in os.environ for name in ("JAINAM_USER_ID", "JAINAM_USER_SESSION")):
                return {
                    "login_state": "environment_override",
                    "message": "Clear old JAINAM_USER_ID / JAINAM_USER_SESSION variables, then open Connect.",
                }
            if self.state == "running":
                return {
                    "login_state": "running",
                    "message": "Finish Jainam sign-in in your browser, then ask again.",
                }
            if self.state == "failed":
                return {
                    "login_state": "failed",
                    "message": "Sign-in failed. Run jainam-mcp connect locally to retry.",
                }
            try:
                app = load_app(self.path)
            except ConfigError:
                app = None
            if app is None:
                return {
                    "login_state": "setup_required",
                    "message": "Run jainam-mcp connect once in Terminal.",
                }
            if not app.automatic_login:
                return {
                    "login_state": "manual_required",
                    "message": "Run jainam-mcp connect --manual locally.",
                }
            self.state = "running"
            threading.Thread(target=self._run, args=(app,), daemon=True).start()
            return {
                "login_state": "running",
                "message": "Finish Jainam sign-in in your browser, then ask again.",
            }

    def _run(self, app):
        state = "failed"
        try:
            credentials = self.authorize(app)
            save(credentials, self.path)
            state = "ready"
        except Exception:
            # No raw errors, credential values or protocol output from this thread.
            pass
        finally:
            with self.lock:
                self.state = state
