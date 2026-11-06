$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 LOCAL ASSEMBLY PERFORMANCE ==="

& $Py -c @'
import time
from father_fua.full_assembly import FullFUAAssemblyRuntime
from father_fua.performance import PerformanceSample, summarize

samples=[]
for i in range(20):
    fua=FullFUAAssemblyRuntime()
    start=time.perf_counter()
    result=fua.run("FATHER universal agent architecture")
    elapsed=(time.perf_counter()-start)*1000
    samples.append(PerformanceSample(elapsed,result.status=="PASS"))

s=summarize(samples)
print(f"COUNT        : {s.count}")
print(f"SUCCESS RATE : {s.success_rate:.3f}")
print(f"P50 MS       : {s.p50_latency_ms:.3f}")
print(f"P95 MS       : {s.p95_latency_ms:.3f}")
if s.success_rate != 1.0:
    raise SystemExit(40)
'@
if ($LASTEXITCODE -ne 0) { throw "performance test failed" }
Write-Host "LOCAL ASSEMBLY PERFORMANCE RESULT: PASS"
