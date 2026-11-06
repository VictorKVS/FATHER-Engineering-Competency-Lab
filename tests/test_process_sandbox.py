def test_process_sandbox_module_imports():
    import father_fua.process_sandbox as module
    assert hasattr(module, "WindowsProcessSandbox")


import os
import sys
import time

import pytest

from father_fua.process_sandbox import WindowsProcessSandbox


def test_process_sandbox_executes_allowlisted_python():
    sb=WindowsProcessSandbox(allowed_executables=[sys.executable],timeout_seconds=5)
    r=sb.run(sys.executable,["-c","print('PASS')"])
    assert r.returncode==0
    assert r.stdout.strip()=="PASS"
    assert r.timed_out is False


def test_process_sandbox_rejects_non_allowlisted_executable():
    sb=WindowsProcessSandbox(allowed_executables=[sys.executable],timeout_seconds=5)
    with pytest.raises(PermissionError):
        sb.run("cmd.exe",["/c","echo nope"])


def test_process_sandbox_scrubs_parent_environment(monkeypatch):
    monkeypatch.setenv("FUA_PARENT_CANARY","CANARY")
    sb=WindowsProcessSandbox(allowed_executables=[sys.executable],timeout_seconds=5)
    code="import os; print(os.environ.get('FUA_PARENT_CANARY','MISSING'))"
    r=sb.run(sys.executable,["-c",code])
    assert r.stdout.strip()=="MISSING"


def test_process_sandbox_times_out():
    sb=WindowsProcessSandbox(allowed_executables=[sys.executable],timeout_seconds=0.2)
    r=sb.run(sys.executable,["-c","import time; time.sleep(5)"])
    assert r.timed_out is True



def test_process_sandbox_preserves_minimal_windows_runtime_env():
    sb=WindowsProcessSandbox(allowed_executables=[sys.executable],timeout_seconds=5)
    code="import os,sys; print(bool(os.environ.get('SystemRoot'))); print(sys.version_info[:2])"
    r=sb.run(sys.executable,["-c",code])
    assert r.returncode==0
    assert "True" in r.stdout



def test_process_sandbox_rejects_invalid_resource_limits():
    with pytest.raises(ValueError):
        WindowsProcessSandbox(allowed_executables=[sys.executable],active_process_limit=0)
    with pytest.raises(ValueError):
        WindowsProcessSandbox(allowed_executables=[sys.executable],process_memory_limit_mb=0)
    with pytest.raises(ValueError):
        WindowsProcessSandbox(allowed_executables=[sys.executable],job_memory_limit_mb=-1)


@pytest.mark.skipif(os.name != "nt", reason="Windows Job Object enforcement")
def test_process_sandbox_job_blocks_second_process():
    sb=WindowsProcessSandbox(
        allowed_executables=[sys.executable],
        timeout_seconds=5,
        active_process_limit=2,
    )
    code=(
        "import subprocess,sys; "
        "\ntry: subprocess.run([sys.executable,'-c','print(1)'],check=True,capture_output=True)"
        "\nexcept Exception as e: print('SPAWN=DENIED',type(e).__name__)"
        "\nelse: print('SPAWN=ALLOWED')"
    )
    r=sb.run(sys.executable,["-c",code])
    assert "SPAWN=DENIED" in r.stdout
    assert "SPAWN=ALLOWED" not in r.stdout



@pytest.mark.skipif(os.name != "nt", reason="Windows venv topology")
def test_windows_venv_two_process_baseline():
    sb=WindowsProcessSandbox(
        allowed_executables=[sys.executable],
        timeout_seconds=5,
        active_process_limit=2,
    )
    r=sb.run(sys.executable,["-c","print('VENV_BASELINE=PASS')"])
    assert r.returncode==0
    assert "VENV_BASELINE=PASS" in r.stdout
