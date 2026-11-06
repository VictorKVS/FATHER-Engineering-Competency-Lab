$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 FLIGHT TEST 05 / RESOURCE & PERFORMANCE ENVELOPE ==="

$Manifest = Get-Content (Join-Path $Repo "factory\chassis\FUA-001\manifest.json") -Raw | ConvertFrom-Json
if ($Manifest.status -ne "PRODUCTION_RELEASED") { throw "performance flight requires PRODUCTION_RELEASED" }
if ($Manifest.production_ready -ne $true) { throw "performance flight requires production_ready=true" }
if ($Manifest.approved_execution_profiles -notcontains "DOCKER_CONTAINED_ONLY") {
    throw "performance flight requires DOCKER_CONTAINED_ONLY"
}

Write-Host ""
Write-Host "01. 200-mission integrated envelope"
& $Py -m pytest tests/test_flight_performance_fua001.py -q
if ($LASTEXITCODE -ne 0) { throw "integrated performance envelope failed" }
Write-Host "INTEGRATED ENVELOPE : PASS"

Write-Host ""
Write-Host "02. Real-model performance run"
$TempPy = Join-Path $env:TEMP "fua-flight-05-performance.py"
@'
import statistics
import time

from father_fua.local_models import discover_local_models
from father_fua.real_model_runtime import RealModelMissionRuntime
from father_fua.evidence import verify_evidence

models=discover_local_models()
if not models:
    print("REAL MODEL PERFORMANCE: BLOCKED - NO_LOCAL_MODEL")
    raise SystemExit(30)

runtime=RealModelMissionRuntime(discoverer=lambda:models)
selected=runtime.choose_model()
print("SELECTED MODEL      :",selected.model_id)

missions=[
    "Performance sortie {:02d}: answer with one short safe-agent engineering principle.".format(i)
    for i in range(1,31)
]

latencies=[]
ids=set()
evidence_ids=set()

for idx,mission in enumerate(missions,1):
    started=time.perf_counter()
    r=runtime.run(mission,timeout=300.0)
    elapsed=int((time.perf_counter()-started)*1000)
    latencies.append(elapsed)

    if not r.audit_ok or not verify_evidence(r.evidence) or not r.response:
        raise SystemExit(31)
    if r.mission_id in ids or r.evidence.evidence_id in evidence_ids:
        raise SystemExit(32)

    ids.add(r.mission_id)
    evidence_ids.add(r.evidence.evidence_id)

    print("SORTIE {:02d} LATENCY_MS={} LEN={} AUDIT={} EVIDENCE={}".format(
        idx,elapsed,len(r.response),r.audit_ok,verify_evidence(r.evidence)
    ))

if not runtime.audit.verify():
    raise SystemExit(33)

ordered=sorted(latencies)
avg=int(sum(latencies)/len(latencies))
p50=int(statistics.median(ordered))
p95=ordered[max(0,int(len(ordered)*0.95)-1)]
p99=ordered[-1]
mx=max(ordered)

print("SORTIE COUNT        :",len(latencies))
print("SUCCESS RATE        : 1.000")
print("AVG LATENCY MS      :",avg)
print("P50 LATENCY MS      :",p50)
print("P95 LATENCY MS      :",p95)
print("P99 LATENCY MS      :",p99)
print("MAX LATENCY MS      :",mx)
print("AUDIT CHAIN         : PASS")
print("REAL MODEL PERF     : PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}
if ($Code -ne 0) { throw "real model performance run failed with exit code $Code" }

Write-Host ""
Write-Host "03. Windows resource boundary"
& (Join-Path $PSScriptRoot "test-fua-sandbox-resource-limits-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "Windows resource boundary failed" }
Write-Host "WINDOWS RESOURCES   : PASS"

Write-Host ""
Write-Host "04. Docker resource boundary"
& (Join-Path $PSScriptRoot "test-fua-docker-native-containment-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "Docker resource boundary failed" }
Write-Host "DOCKER RESOURCES    : PASS"

Write-Host ""
Write-Host "05. Reliability regression"
& (Join-Path $PSScriptRoot "test-fua-reliability-gate-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "reliability regression failed" }
Write-Host "RELIABILITY         : PASS"

Write-Host ""
Write-Host "06. Flight recorder integrity"
& (Join-Path $PSScriptRoot "test-fua-final-evidence-audit.ps1")
if ($LASTEXITCODE -ne 0) { throw "flight recorder audit failed" }
Write-Host "FLIGHT RECORDER     : PASS"

Write-Host ""
Write-Host "FUA-001 FLIGHT TEST 05 RESULT: PASS"
