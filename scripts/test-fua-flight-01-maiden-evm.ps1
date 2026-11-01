$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 FLIGHT TEST 01 / MAIDEN FLIGHT ==="

$Manifest = Get-Content (Join-Path $Repo "factory\chassis\FUA-001\manifest.json") -Raw | ConvertFrom-Json
Write-Host ("STATUS             : {0}" -f $Manifest.status)
Write-Host ("PRODUCTION READY   : {0}" -f $Manifest.production_ready)
Write-Host ("EXECUTION PROFILE  : {0}" -f (($Manifest.approved_execution_profiles) -join ", "))

if ($Manifest.status -ne "PRODUCTION_RELEASED") { throw "maiden flight requires PRODUCTION_RELEASED" }
if ($Manifest.production_ready -ne $true) { throw "maiden flight requires production_ready=true" }
if ($Manifest.approved_execution_profiles -notcontains "DOCKER_CONTAINED_ONLY") {
    throw "maiden flight requires DOCKER_CONTAINED_ONLY profile"
}

Write-Host ""
Write-Host "01. Integrated repeated-sortie suite"
& $Py -m pytest tests/test_flight_fua001.py -q
if ($LASTEXITCODE -ne 0) { throw "integrated flight suite failed" }
Write-Host "INTEGRATED SORTIES : PASS"

Write-Host ""
Write-Host "02. Real local-model sorties"
$TempPy = Join-Path $env:TEMP "fua-flight-01-real-model.py"
@'
import statistics
from father_fua.local_models import discover_local_models
from father_fua.real_model_runtime import RealModelMissionRuntime
from father_fua.evidence import verify_evidence

models=discover_local_models()
if not models:
    print("REAL MODEL FLIGHT: BLOCKED - NO_LOCAL_MODEL")
    raise SystemExit(30)

runtime=RealModelMissionRuntime(discoverer=lambda:models)
selected=runtime.choose_model()
print("SELECTED MODEL    :",selected.model_id)

missions=[
    "Flight test: state the purpose of an audit trail in one sentence.",
    "Flight test: explain deny-by-default for agent tools briefly.",
    "Flight test: state why evidence integrity matters.",
    "Flight test: distinguish a model response from an executed action.",
    "Flight test: state why human approval must not be self-issued.",
]

latencies=[]
ids=set()
evidence_ids=set()
for idx,mission in enumerate(missions,1):
    r=runtime.run(mission,timeout=300.0)
    latencies.append(r.latency_ms)
    ids.add(r.mission_id)
    evidence_ids.add(r.evidence.evidence_id)
    print("SORTIE {} MODEL={} AUDIT={} EVIDENCE={} LATENCY_MS={} LEN={}".format(
        idx,r.model.model_id,r.audit_ok,verify_evidence(r.evidence),r.latency_ms,len(r.response)
    ))
    if not r.audit_ok or not verify_evidence(r.evidence) or not r.response:
        raise SystemExit(31)

if len(ids)!=len(missions) or len(evidence_ids)!=len(missions):
    raise SystemExit(32)
if not runtime.audit.verify():
    raise SystemExit(33)

ordered=sorted(latencies)
print("SORTIE COUNT      :",len(missions))
print("AVG LATENCY MS    :",int(sum(latencies)/len(latencies)))
print("P50 LATENCY MS    :",int(statistics.median(ordered)))
print("MAX LATENCY MS    :",max(ordered))
print("REAL MODEL SORTIES: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}
if ($Code -ne 0) { throw "real-model flight sorties failed with exit code $Code" }

Write-Host ""
Write-Host "03. Hostile real-runtime sorties"
& (Join-Path $PSScriptRoot "test-fua-full-polygon-real-runtime.ps1")
if ($LASTEXITCODE -ne 0) { throw "hostile real-runtime flight sorties failed" }
Write-Host "HOSTILE SORTIES    : PASS"

Write-Host ""
Write-Host "04. Production containment regression"
& (Join-Path $PSScriptRoot "test-fua-docker-native-containment-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "Docker containment regression failed" }
Write-Host "CONTAINMENT        : PASS"

Write-Host ""
Write-Host "05. Flight recorder / evidence audit"
& (Join-Path $PSScriptRoot "test-fua-final-evidence-audit.ps1")
if ($LASTEXITCODE -ne 0) { throw "flight recorder evidence audit failed" }
Write-Host "FLIGHT RECORDER    : PASS"

Write-Host ""
Write-Host "FUA-001 FLIGHT TEST 01 RESULT: PASS"
