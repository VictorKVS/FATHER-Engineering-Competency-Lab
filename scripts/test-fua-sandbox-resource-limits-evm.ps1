$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 WINDOWS SANDBOX RESOURCE LIMITS EVM ==="

$TempPy = Join-Path $env:TEMP "fua-resource-limits-evm.py"

@'
import os
import sys
from father_fua.process_sandbox import WindowsProcessSandbox

print("01. ACTIVE PROCESS LIMIT (VENV LAUNCHER + BASE INTERPRETER)")
sb=WindowsProcessSandbox(
    allowed_executables=[sys.executable],
    timeout_seconds=5,
    active_process_limit=2,
    process_memory_limit_mb=256,
    job_memory_limit_mb=384,
)
code=(
    "import subprocess,sys; "
    "\ntry: subprocess.run([sys.executable,'-c','print(1)'],check=True,capture_output=True)"
    "\nexcept Exception as e: print('CHILD_SPAWN=DENIED'); print('ERROR_TYPE='+type(e).__name__)"
    "\nelse: print('CHILD_SPAWN=ALLOWED')"
)
r=sb.run(sys.executable,["-c",code])
print(r.stdout.strip())
if "CHILD_SPAWN=DENIED" not in r.stdout or "CHILD_SPAWN=ALLOWED" in r.stdout:
    raise SystemExit(20)

print("")
print("02. PROCESS MEMORY LIMIT")
mem=WindowsProcessSandbox(
    allowed_executables=[sys.executable],
    timeout_seconds=10,
    active_process_limit=2,
    process_memory_limit_mb=96,
    job_memory_limit_mb=128,
)
code=(
    "import sys; "
    "\ntry: x=bytearray(256*1024*1024); print('MEMORY_LIMIT=FAIL')"
    "\nexcept MemoryError: print('MEMORY_LIMIT=PASS')"
)
r=mem.run(sys.executable,["-c",code])
print("RETURN_CODE     :",r.returncode)
print("STDOUT          :",r.stdout.strip())
print("STDERR          :",r.stderr.strip())
memory_blocked=("MEMORY_LIMIT=PASS" in r.stdout) or (r.returncode != 0 and "MEMORY_LIMIT=FAIL" not in r.stdout)
if not memory_blocked:
    raise SystemExit(21)

print("")
print("WINDOWS SANDBOX RESOURCE LIMITS EVM RESULT: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) {
    throw "sandbox resource-limits EVM failed with exit code $Code"
}
