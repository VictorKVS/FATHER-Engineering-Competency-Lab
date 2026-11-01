$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 FLIGHT TEST 03 / TURBULENCE & FAULT INJECTION ==="

$Manifest = Get-Content (Join-Path $Repo "factory\chassis\FUA-001\manifest.json") -Raw | ConvertFrom-Json
if ($Manifest.status -ne "PRODUCTION_RELEASED") { throw "fault flight requires PRODUCTION_RELEASED" }
if ($Manifest.production_ready -ne $true) { throw "fault flight requires production_ready=true" }
if ($Manifest.approved_execution_profiles -notcontains "DOCKER_CONTAINED_ONLY") {
    throw "fault flight requires DOCKER_CONTAINED_ONLY"
}

Write-Host ""
Write-Host "01. Deterministic fault-injection suite"
& $Py -m pytest tests/test_flight_fault_injection_fua001.py tests/test_reliability_failure_injection.py tests/test_reliability_stress.py -q
if ($LASTEXITCODE -ne 0) { throw "fault-injection regression failed" }
Write-Host "FAULT SUITE         : PASS"

Write-Host ""
Write-Host "02. Real-model timeout / recovery contract"
$TempPy = Join-Path $env:TEMP "fua-flight-03-model-faults.py"
@'
from father_fua.local_models import DiscoveredModel
from father_fua.real_model_runtime import RealModelMissionRuntime

model=DiscoveredModel(
    transport="OLLAMA",
    base_url="http://127.0.0.1:11434",
    model_id="FAULT-SIM-LOCAL",
    local=True,
    healthy=True,
    supports_chat=True,
)

calls={"n":0}

def discoverer():
    return [model]

def invoker(selected,prompt,timeout):
    calls["n"]+=1
    if calls["n"]==1:
        raise TimeoutError("synthetic cold-start timeout")
    return "RECOVERED_AFTER_TIMEOUT"

runtime=RealModelMissionRuntime(discoverer=discoverer,invoker=invoker)
r=runtime.run("fault injection recovery sortie",timeout=0.1)

print("CALL COUNT          :",calls["n"])
print("RESPONSE            :",r.response)
print("AUDIT               :",r.audit_ok)
print("RECOVERY            :","PASS" if calls["n"]==2 and r.audit_ok and r.response=="RECOVERED_AFTER_TIMEOUT" else "FAIL")

if calls["n"]!=2 or not r.audit_ok or r.response!="RECOVERED_AFTER_TIMEOUT":
    raise SystemExit(31)

def hard_fail(selected,prompt,timeout):
    raise RuntimeError("synthetic hard failure")

failed=RealModelMissionRuntime(discoverer=discoverer,invoker=hard_fail)
try:
    failed.run("hard failure sortie",timeout=0.1)
except RuntimeError:
    print("HARD FAILURE ESCAPE : PASS")
else:
    raise SystemExit(32)

print("MODEL FAULT CONTRACT: PASS")
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}
if ($Code -ne 0) { throw "model fault contract failed with exit code $Code" }

Write-Host ""
Write-Host "03. Fault / recovery stress"
& (Join-Path $PSScriptRoot "test-fua-fault-recovery-stress-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "fault recovery stress failed" }
Write-Host "FAULT RECOVERY      : PASS"

Write-Host ""
Write-Host "04. Hostile boundary under turbulence"
& (Join-Path $PSScriptRoot "test-fua-full-polygon-real-runtime.ps1")
if ($LASTEXITCODE -ne 0) { throw "security boundary failed under turbulence" }
Write-Host "SECURITY BOUNDARY   : PASS"

Write-Host ""
Write-Host "05. Containment after faults"
& (Join-Path $PSScriptRoot "test-fua-docker-native-containment-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "containment failed after faults" }
Write-Host "CONTAINMENT         : PASS"

Write-Host ""
Write-Host "06. Flight recorder integrity"
& (Join-Path $PSScriptRoot "test-fua-final-evidence-audit.ps1")
if ($LASTEXITCODE -ne 0) { throw "flight recorder failed after turbulence" }
Write-Host "FLIGHT RECORDER     : PASS"

Write-Host ""
Write-Host "FUA-001 FLIGHT TEST 03 RESULT: PASS"
