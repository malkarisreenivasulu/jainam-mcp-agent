"""Local double-click launcher: prepare the isolated install, then connect."""

import os
import subprocess
import sys
import venv
from pathlib import Path


def main():
    if sys.version_info < (3, 11):  # noqa: UP036 - launcher can run before package installation
        print("Please install Python 3.11 or newer from python.org, then open Connect again.")
        return 1
    import tomllib

    root = Path(__file__).resolve().parents[1]
    python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        print("Preparing Jainam for first use. This may take a few minutes.", flush=True)
        venv.create(root / ".venv", with_pip=True)
    expected = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    version = subprocess.run(
        [str(python), "-m", "jainam_mcp", "--version"], capture_output=True, text=True, cwd=root
    )
    if version.returncode or version.stdout.strip() != expected:
        result = subprocess.run([str(python), "-m", "pip", "install", "."], cwd=root)
        if result.returncode:
            print("Installation could not finish. Check internet access and try again.")
            return result.returncode
    return subprocess.call([str(python), "-m", "jainam_mcp", "connect", *sys.argv[1:]], cwd=root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError):
        print("Cannot prepare the local installation. Check Python and folder permissions.")
        raise SystemExit(1) from None
