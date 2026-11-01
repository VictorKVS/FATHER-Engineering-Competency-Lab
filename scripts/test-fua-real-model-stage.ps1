$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 REAL MODEL STAGE ==="

& $Py -c @'
from father_fua.local_models import discover_local_models
from father_fua.model_compatibility import evaluate_local_model
from father_fua.real_model_runtime import RealModelMissionRuntime

models = discover_local_models()
print(f"DISCOVERED      : {len(models)}")
if not models:
    raise SystemExit(20)

compatible = []
for i, model in enumerate(models, 1):
    result = evaluate_local_model(model, prompt_chars=1000)
    print(
        f"{i}. transport={model.transport} model={model.model_id} "
        f"url={model.base_url} compatibility={result.status}"
    )
    if result.status == "PASS":
        compatible.append(model)

if not compatible:
    raise SystemExit(21)

selected = compatible[0]
runtime = RealModelMissionRuntime(
    discoverer=lambda: [selected]
)
result = runtime.run(
    "In one short paragraph, explain what a universal AI agent chassis is. "
    "Do not claim to have used external tools."
)

print("")
print(f"SELECTED MODEL  : {selected.model_id}")
print(f"TRANSPORT       : {selected.transport}")
print(f"MODEL URL       : {selected.base_url}")
print(f"MISSION STATUS  : PASS")
print(f"AUDIT OK        : {result.audit_ok}")
print(f"LATENCY MS      : {result.latency_ms}")
print(f"RESPONSE SHA256 : {result.response_sha256}")
print(f"EVIDENCE SHA256 : {result.evidence.sha256}")
print(f"RESPONSE LENGTH : {len(result.response)}")
print("--- RESPONSE ---")
print(result.response[:2000])

if not result.audit_ok:
    raise SystemExit(22)
'@

$Code = $LASTEXITCODE
if ($Code -eq 20) {
    Write-Host ""
    Write-Host "REAL MODEL STAGE: BLOCKED - NO LOCAL MODEL SERVICE DISCOVERED"
    exit 20
}
if ($Code -eq 21) {
    Write-Host ""
    Write-Host "REAL MODEL STAGE: BLOCKED - NO COMPATIBLE LOCAL MODEL"
    exit 21
}
if ($Code -ne 0) {
    throw "real model stage failed with exit code $Code"
}

Write-Host ""
Write-Host "REAL MODEL STAGE RESULT: PASS"
