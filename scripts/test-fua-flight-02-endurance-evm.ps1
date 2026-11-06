$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 FLIGHT TEST 02 / ENDURANCE SOAK ==="

$Manifest = Get-Content (Join-Path $Repo "factory\chassis\FUA-001\manifest.json") -Raw | ConvertFrom-Json
if ($Manifest.status -ne "PRODUCTION_RELEASED") { throw "endurance requires PRODUCTION_RELEASED" }
if ($Manifest.production_ready -ne $true) { throw "endurance requires production_ready=true" }
if ($Manifest.approved_execution_profiles -notcontains "DOCKER_CONTAINED_ONLY") {
    throw "endurance requires DOCKER_CONTAINED_ONLY"
}

Write-Host ""
Write-Host "01. 100-mission integrated soak"
& $Py -m pytest tests/test_flight_endurance_fua001.py -q
if ($LASTEXITCODE -ne 0) { throw "integrated endurance suite failed" }
Write-Host "INTEGRATED SOAK    : PASS"

Write-Host ""
Write-Host "02. Real-model endurance loop"
$TempPy = Join-Path $env:TEMP "fua-flight-02-real-model.py"
@'
import statistics
from father_fua.local_models import discover_local_models
from father_fua.real_model_runtime import RealModelMissionRuntime
from father_fua.evidence import verify_evidence

models=discover_local_models()
if not models:
    print("REAL MODEL ENDURANCE: BLOCKED - NO_LOCAL_MODEL")
    raise SystemExit(30)

runtime=RealModelMissionRuntime(discoverer=lambda:models)
selected=runtime.choose_model()
print("SELECTED MODEL      :",selected.model_id)

missions=[
    "Endurance sortie {:02d}: state one safe-agent engineering principle in one sentence.".format(i)
    for i in range(1,21)
]

latencies=[]
mission_ids=set()
evidence_ids=set()
for idx,mission in enumerate(missions,1):
    r=runtime.run(mission,timeout=300.0)
    ok=r.audit_ok and verify_evidence(r.evidence) and bool(r.response)
    print("SORTIE {:02d} AUDIT={} EVIDENCE={} LATENCY_MS={} LEN={}".format(
        idx,r.audit_ok,verify_evidence(r.evidence),r.latency_ms,len(r.response)
    ))
    if not ok:
        raise SystemExit(31)
    if r.mission_id in mission_ids or r.evidence.evidence_id in evidence_ids:
        raise SystemExit(32)
    mission_ids.add(r.mission_id)
    evidence_ids.add(r.evidence.evidence_id)
    latencies.append(r.latency_ms)

if not runtime.audit.verify():
    raise SystemExit(33)

ordered=sorted(latencies)
avg=int(sum(latencies)/len(latencies))
p50=int(statistics.median(ordered))
p95=ordered[max(0,int(len(ordered)*0.95)-1)]
mx=max(ordered)

print("SORTIE COUNT        :",len(latencies))
print("SUCCESS RATE        : 1.000")
print("AVG LATENCY MS      :",avg)
print("P50 LATENCY MS      :",p50)
print("P95 LATENCY MS      :",p95)
print("MAX LATENCY MS      :",mx)
print("AUDIT CHAIN         : PASS")
print("REAL MODEL ENDURANCE: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}
if ($Code -ne 0) { throw "real-model endurance failed with exit code $Code" }

Write-Host ""
Write-Host "03. Reliability regression"
& (Join-Path $PSScriptRoot "test-fua-reliability-gate-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "reliability regression failed" }
Write-Host "RELIABILITY         : PASS"

Write-Host ""
Write-Host "04. Security boundary regression"
& (Join-Path $PSScriptRoot "test-fua-full-polygon-real-runtime.ps1")
if ($LASTEXITCODE -ne 0) { throw "security boundary regression failed" }
Write-Host "SECURITY BOUNDARY   : PASS"

Write-Host ""
Write-Host "05. Containment regression"
& (Join-Path $PSScriptRoot "test-fua-docker-native-containment-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "containment regression failed" }
Write-Host "CONTAINMENT         : PASS"

Write-Host ""
Write-Host "06. Flight recorder"
& (Join-Path $PSScriptRoot "test-fua-final-evidence-audit.ps1")
if ($LASTEXITCODE -ne 0) { throw "evidence audit failed" }
Write-Host "FLIGHT RECORDER     : PASS"

Write-Host ""
Write-Host "FUA-001 FLIGHT TEST 02 RESULT: PASS"
