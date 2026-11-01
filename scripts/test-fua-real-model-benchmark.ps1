$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 REAL MODEL BENCHMARK ==="

$TempPy = Join-Path $env:TEMP "fua-real-model-benchmark.py"
@'
import statistics
import time

from father_fua.local_models import discover_local_models
from father_fua.real_model_runtime import RealModelMissionRuntime

models=discover_local_models()
if not models:
    raise SystemExit(20)

runtime=RealModelMissionRuntime(discoverer=lambda:models)
selected=runtime.choose_model()
print("SELECTED MODEL  : {}".format(selected.model_id))

missions=[
    "Define an AI agent in one sentence.",
    "List three properties of a safe universal agent chassis.",
    "Explain why audit evidence matters in one short paragraph.",
    "State one reason to keep model routing provider-independent.",
    "Explain why deny-by-default is useful for tool execution.",
]

latencies=[]
hashes=[]
for i,mission in enumerate(missions,1):
    started=time.perf_counter()
    r=runtime.run(mission,timeout=300.0)
    elapsed=int((time.perf_counter()-started)*1000)
    latencies.append(elapsed)
    hashes.append(r.response_sha256)
    print("RUN {} STATUS={} AUDIT={} LATENCY_MS={} LEN={} SHA={}".format(
        i,r.status,r.audit_ok,elapsed,len(r.response),r.response_sha256
    ))
    if r.status!="PASS" or not r.audit_ok or not r.response:
        raise SystemExit(21)

ordered=sorted(latencies)
p50=int(statistics.median(ordered))
p95=ordered[-1]
avg=int(sum(ordered)/len(ordered))

print("")
print("COUNT           : {}".format(len(latencies)))
print("SUCCESS RATE    : 1.000")
print("AVG MS          : {}".format(avg))
print("P50 MS          : {}".format(p50))
print("P95 MS          : {}".format(p95))
print("UNIQUE HASHES   : {}".format(len(set(hashes))))
print("")
print("REAL MODEL BENCHMARK RESULT: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if($Code -ne 0){ throw "real model benchmark failed with exit code $Code" }
