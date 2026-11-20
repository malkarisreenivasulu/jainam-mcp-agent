import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import Mock


def launcher(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "scripts" / "connect.py"
    spec = importlib.util.spec_from_file_location("connect_launcher", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "__file__", str(tmp_path / "scripts" / "connect.py"))
    (tmp_path / "pyproject.toml").write_text('[project]\nversion="0.1.5"\n')
    monkeypatch.setattr(module.sys, "argv", ["connect.py"])
    python = tmp_path / ".venv" / ("Scripts/python.exe" if module.os.name == "nt" else "bin/python")
    python.parent.mkdir(parents=True)
    python.touch()
    return module


def test_launcher_reuses_installed_version_without_install(tmp_path, monkeypatch):
    module = launcher(tmp_path, monkeypatch)
    run = Mock(return_value=subprocess.CompletedProcess([], 0, "0.1.5\n", ""))
    call = Mock(return_value=0)
    monkeypatch.setattr(module.subprocess, "run", run)
    monkeypatch.setattr(module.subprocess, "call", call)
    assert module.main() == 0
    assert run.call_count == 1
    assert call.call_args.args[0][-1] == "connect"


def test_failed_install_does_not_attempt_login(tmp_path, monkeypatch):
    module = launcher(tmp_path, monkeypatch)
    run = Mock(side_effect=[subprocess.CompletedProcess([], 1, "", ""), subprocess.CompletedProcess([], 1)])
    call = Mock()
    monkeypatch.setattr(module.subprocess, "run", run)
    monkeypatch.setattr(module.subprocess, "call", call)
    assert module.main() == 1
    call.assert_not_called()
