$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 WINDOWS SANDBOX STRESS EVM ==="

$TempPy = Join-Path $env:TEMP "fua-sandbox-stress-evm.py"

@'
import sys
from father_fua.process_sandbox import WindowsProcessSandbox

normal_pass=0
spawn_denied=0
timeout_pass=0

print("01. REPEATED ALLOWLISTED EXECUTION")
for i in range(20):
    sb=WindowsProcessSandbox(
        allowed_executables=[sys.executable],
        timeout_seconds=3,
        active_process_limit=2,
        process_memory_limit_mb=256,
        job_memory_limit_mb=384,
    )
    r=sb.run(sys.executable,["-c",f"print('RUN={i}')"])
    if r.returncode == 0 and f"RUN={i}" in r.stdout and not r.timed_out:
        normal_pass += 1
print("ALLOWLIST PASS  :",normal_pass,"/20")
if normal_pass != 20:
    raise SystemExit(20)

print("")
print("02. REPEATED CHILD-PROCESS DENIAL")
code=(
    "import subprocess,sys; "
    "\ntry: subprocess.run([sys.executable,'-c','print(1)'],check=True,capture_output=True)"
    "\nexcept Exception: print('SPAWN=DENIED')"
    "\nelse: print('SPAWN=ALLOWED')"
)
for _ in range(20):
    sb=WindowsProcessSandbox(
        allowed_executables=[sys.executable],
        timeout_seconds=3,
        active_process_limit=2,
        process_memory_limit_mb=256,
        job_memory_limit_mb=384,
    )
    r=sb.run(sys.executable,["-c",code])
    if "SPAWN=DENIED" in r.stdout and "SPAWN=ALLOWED" not in r.stdout:
        spawn_denied += 1
print("SPAWN DENIED    :",spawn_denied,"/20")
if spawn_denied != 20:
    raise SystemExit(21)

print("")
print("03. REPEATED TIMEOUT TERMINATION")
for _ in range(5):
    sb=WindowsProcessSandbox(
        allowed_executables=[sys.executable],
        timeout_seconds=0.2,
        active_process_limit=2,
        process_memory_limit_mb=256,
        job_memory_limit_mb=384,
    )
    r=sb.run(sys.executable,["-c","import time; time.sleep(2)"])
    if r.timed_out:
        timeout_pass += 1
print("TIMEOUT PASS    :",timeout_pass,"/5")
if timeout_pass != 5:
    raise SystemExit(22)

print("")
print("WINDOWS SANDBOX STRESS EVM RESULT: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) {
    throw "sandbox stress EVM failed with exit code $Code"
}
