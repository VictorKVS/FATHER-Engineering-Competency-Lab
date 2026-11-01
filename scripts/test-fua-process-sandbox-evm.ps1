$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 WINDOWS PROCESS SANDBOX EVM ==="

$TempPy = Join-Path $env:TEMP "fua-process-sandbox-evm.py"
@'
import os
import sys
from father_fua.process_sandbox import WindowsProcessSandbox

sb=WindowsProcessSandbox(
    allowed_executables=[sys.executable],
    timeout_seconds=3,
    max_output_chars=4096,
)

print("01. ALLOWLISTED PROCESS")
r=sb.run(sys.executable,["-c","import os; print('SANDBOX='+os.environ.get('FUA_SANDBOX','0')); print('CWD='+os.getcwd())"])
print("RETURN_CODE     : {}".format(r.returncode))
print("TIMED_OUT       : {}".format(r.timed_out))
print("STDOUT          : {}".format(r.stdout.strip()))
print("STDERR          : {}".format(r.stderr.strip()))
if r.returncode != 0 or r.timed_out or "SANDBOX=1" not in r.stdout:
    raise SystemExit(20)

print("")
print("02. ENVIRONMENT LEAK TEST")
os.environ["FUA_PARENT_SECRET"]="SHOULD_NOT_LEAK"
r=sb.run(sys.executable,["-c","import os; print(os.environ.get('FUA_PARENT_SECRET','MISSING'))"])
print("SECRET_VISIBLE  : {}".format(r.stdout.strip()))
if r.stdout.strip() != "MISSING":
    raise SystemExit(21)

print("")
print("03. EXECUTABLE DENY TEST")
try:
    sb.run("cmd.exe",["/c","echo SHOULD_NOT_RUN"])
except PermissionError:
    print("CMD_DENY        : PASS")
else:
    raise SystemExit(22)

print("")
print("04. TIMEOUT / TERMINATION TEST")
slow=WindowsProcessSandbox(allowed_executables=[sys.executable],timeout_seconds=0.5,max_output_chars=4096)
r=slow.run(sys.executable,["-c","import time; time.sleep(30)"])
print("TIMED_OUT       : {}".format(r.timed_out))
if not r.timed_out:
    raise SystemExit(23)

print("")
print("WINDOWS PROCESS SANDBOX EVM RESULT: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}
if($Code -ne 0){ throw "process sandbox EVM failed with exit code $Code" }
