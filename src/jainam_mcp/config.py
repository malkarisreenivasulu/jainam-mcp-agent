"""Local credentials; never searched for in a project or exposed as MCP arguments."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """A safe-to-display configuration error (contains no credential values)."""


def default_path() -> Path:
    root = (
        Path(os.environ["APPDATA"])
        if os.name == "nt" and os.environ.get("APPDATA")
        else Path.home() / ".config"
    )
    return root / "jainam-mcp" / "credentials.json"


@dataclass(frozen=True, repr=False)
class Credentials:
    user_id: str
    user_session: str

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip() for v in (self.user_id, self.user_session)):
            raise ConfigError("Both user ID and user session must be nonempty strings.")
        if any("\n" in v or "\r" in v for v in (self.user_id, self.user_session)):
            raise ConfigError("Credentials cannot contain line breaks.")


def load(path: Path | None = None) -> Credentials | None:
    user_id, session = os.environ.get("JAINAM_USER_ID"), os.environ.get("JAINAM_USER_SESSION")
    if user_id is not None or session is not None:
        if not user_id or not session:
            raise ConfigError("Set both JAINAM_USER_ID and JAINAM_USER_SESSION, or unset both.")
        return Credentials(user_id, session)
    path = path or default_path()
    if not path.exists():
        return None
    if os.name == "posix" and stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ConfigError("Credentials file must be private. Run chmod 600 on your credentials file.")
    try:
        if path.stat().st_size > 65536:
            raise ValueError
        data = json.loads(path.read_text(encoding="utf-8"))
        return Credentials(data["user_id"], data["user_session"])
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        raise ConfigError("Invalid credentials file. Run jainam-mcp configure again.") from exc


def save(credentials: Credentials, path: Path | None = None) -> Path:
    return save_private(
        {"user_id": credentials.user_id, "user_session": credentials.user_session}, path or default_path()
    )


def save_private(data: dict, path: Path) -> Path:
    if path.is_symlink():
        raise ConfigError("Refusing to replace a symbolic-link credentials file.")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".credentials-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            os.chmod(temporary, 0o600)
            json.dump(data, out)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path


@dataclass(frozen=True, repr=False)
class AppCredentials:
    app_code: str
    api_secret: str
    automatic_login: bool = True

    def __post_init__(self):
        if any(
            not isinstance(v, str) or not v.strip() or "\n" in v or "\r" in v
            for v in (self.app_code, self.api_secret)
        ):
            raise ConfigError("APP Code and Secret Key must be nonempty single-line values.")


def app_path(path: Path | None = None) -> Path:
    return (path or default_path()).with_name(
        path.stem + ".app_credentials.json" if path else "app_credentials.json"
    )


def load_app(path: Path | None = None) -> AppCredentials | None:
    destination = app_path(path)
    if not destination.exists():
        return None
    if os.name == "posix" and stat.S_IMODE(destination.stat().st_mode) & 0o077:
        raise ConfigError("Saved app settings must be private; restrict their permissions to 600.")
    try:
        if destination.stat().st_size > 65536:
            raise ValueError
        data = json.loads(destination.read_text(encoding="utf-8"))
        if not isinstance(data.get("automatic_login", True), bool):
            raise ValueError
        return AppCredentials(data["app_code"], data["api_secret"], data.get("automatic_login", True))
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        raise ConfigError("Invalid saved app settings. Run connect --replace-app.") from exc


def save_app(app: AppCredentials, path: Path | None = None) -> Path:
    return save_private(
        {"app_code": app.app_code, "api_secret": app.api_secret, "automatic_login": app.automatic_login},
        app_path(path),
    )
