$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 REAL MODEL STAGE ==="

$TempPy = Join-Path $env:TEMP "fua-real-model-stage.py"

@'
from father_fua.local_models import discover_local_models
from father_fua.model_compatibility import evaluate_local_model
from father_fua.real_model_runtime import RealModelMissionRuntime

models = discover_local_models()
print("DISCOVERED      : {}".format(len(models)))
if not models:
    raise SystemExit(20)

compatible = []
for i, model in enumerate(models, 1):
    result = evaluate_local_model(model, prompt_chars=1000)
    print(
        "{}. transport={} model={} url={} compatibility={}".format(
            i, model.transport, model.model_id, model.base_url, result.status
        )
    )
    if result.status == "PASS":
        compatible.append(model)

if not compatible:
    raise SystemExit(21)

selected = compatible[0]
runtime = RealModelMissionRuntime(discoverer=lambda: [selected])
print("WARMUP          : starting selected local model")
result = runtime.run(
    "In one short paragraph, explain what a universal AI agent chassis is. "
    "Do not claim to have used external tools.",
    timeout=300.0,
)

print("")
print("SELECTED MODEL  : {}".format(selected.model_id))
print("TRANSPORT       : {}".format(selected.transport))
print("MODEL URL       : {}".format(selected.base_url))
print("MISSION STATUS  : PASS")
print("AUDIT OK        : {}".format(result.audit_ok))
print("LATENCY MS      : {}".format(result.latency_ms))
print("RESPONSE SHA256 : {}".format(result.response_sha256))
print("EVIDENCE SHA256 : {}".format(result.evidence.sha256))
print("RESPONSE LENGTH : {}".format(len(result.response)))
print("--- RESPONSE ---")
print(result.response[:2000])

if not result.audit_ok:
    raise SystemExit(22)
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code = $LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

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
