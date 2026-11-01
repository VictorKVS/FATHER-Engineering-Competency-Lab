$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 REAL LOCAL MODEL MISSION ==="

& $Py -c @'
from father_fua.real_model_runtime import RealModelMissionRuntime

runtime=RealModelMissionRuntime()
model=runtime.choose_model()
print(f"MODEL TRANSPORT : {model.transport}")
print(f"MODEL ID        : {model.model_id}")
print(f"MODEL URL       : {model.base_url}")

result=runtime.run(
    "In one short paragraph, explain what a universal AI agent chassis is. "
    "Do not claim to have used external tools."
)

print(f"MISSION STATUS  : PASS")
print(f"AUDIT OK        : {result.audit_ok}")
print(f"LATENCY MS      : {result.latency_ms}")
print(f"RESPONSE SHA256 : {result.response_sha256}")
print(f"EVIDENCE SHA256 : {result.evidence.sha256}")
print(f"RESPONSE LENGTH : {len(result.response)}")
print("--- RESPONSE ---")
print(result.response[:2000])

if not result.audit_ok:
    raise SystemExit(21)
if len(result.response_sha256) != 64 or len(result.evidence.sha256) != 64:
    raise SystemExit(22)
'@

if ($LASTEXITCODE -ne 0) {
    throw "real local model mission failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "REAL LOCAL MODEL MISSION RESULT: PASS"
