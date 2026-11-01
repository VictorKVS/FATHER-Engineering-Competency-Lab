$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 FLIGHT TEST 06 / CERTIFICATION REVIEW ==="

$ManifestPath = Join-Path $Repo "factory\chassis\FUA-001\manifest.json"
$Manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

if ($Manifest.status -ne "PRODUCTION_RELEASED") { throw "certification requires PRODUCTION_RELEASED" }
if ($Manifest.production_ready -ne $true) { throw "certification requires production_ready=true" }
if ($Manifest.approved_execution_profiles -notcontains "DOCKER_CONTAINED_ONLY") {
    throw "certification requires DOCKER_CONTAINED_ONLY"
}
if ($Manifest.windows_host_native_execution -ne "NOT_APPROVED") {
    throw "Windows host native execution must remain NOT_APPROVED"
}

Write-Host ""
Write-Host "01. Required flight evidence"
$Required = @(
    "factory\evidence\EVID-FUA-FLIGHT-01-MAIDEN-0025.md",
    "factory\evidence\EVID-FUA-FLIGHT-02-ENDURANCE-0026.md",
    "factory\evidence\EVID-FUA-FLIGHT-03-TURBULENCE-0027.md",
    "factory\evidence\EVID-FUA-FLIGHT-04-SECURITY-COMBAT-0028.md",
    "factory\evidence\EVID-FUA-FLIGHT-05-PERFORMANCE-0029.md"
)
foreach ($Rel in $Required) {
    $P = Join-Path $Repo $Rel
    if (-not (Test-Path $P)) { throw "missing flight evidence: $Rel" }
    $Text = Get-Content $P -Raw
    if ($Text -notmatch "Status: PASS") { throw "flight evidence not PASS: $Rel" }
    Write-Host ("PASS : {0}" -f $Rel)
}
Write-Host "FLIGHT EVIDENCE     : PASS"

Write-Host ""
Write-Host "02. Flight program manifest state"
$FP=$Manifest.flight_test_program
if ($null -eq $FP) { throw "flight_test_program missing from manifest" }
if ($FP.maiden_flight.status -ne "PASS") { throw "maiden flight missing PASS" }
if ($FP.endurance.status -ne "PASS") { throw "endurance missing PASS" }
if ($FP.turbulence.status -ne "PASS") { throw "turbulence missing PASS" }
if ($FP.security_combat.status -ne "PASS") { throw "security combat missing PASS" }
if ($FP.performance.status -ne "PASS") { throw "performance missing PASS" }
Write-Host "MANIFEST FLIGHT DATA: PASS"

Write-Host ""
Write-Host "03. Full deterministic regression"
& $Py -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "full deterministic regression failed" }
Write-Host "FULL REGRESSION     : PASS"

Write-Host ""
Write-Host "04. Production reliability gate"
& (Join-Path $PSScriptRoot "test-fua-reliability-gate-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "production reliability gate failed" }
Write-Host "RELIABILITY         : PASS"

Write-Host ""
Write-Host "05. Production containment gate"
& (Join-Path $PSScriptRoot "test-fua-docker-native-containment-evm.ps1")
if ($LASTEXITCODE -ne 0) { throw "production containment gate failed" }
Write-Host "CONTAINMENT         : PASS"

Write-Host ""
Write-Host "06. Final evidence audit"
& (Join-Path $PSScriptRoot "test-fua-final-evidence-audit.ps1")
if ($LASTEXITCODE -ne 0) { throw "final evidence audit failed" }
Write-Host "EVIDENCE AUDIT      : PASS"

Write-Host ""
Write-Host "07. Certification decision"
Write-Host "CERTIFIED PROFILE   : DOCKER_CONTAINED_ONLY"
Write-Host "WINDOWS HOST NATIVE : NOT_APPROVED"
Write-Host "OPEN HIGH/CRITICAL  : 0"
Write-Host "FLIGHT CERTIFICATION: PASS"
Write-Host ""
Write-Host "FUA-001 FLIGHT TEST 06 RESULT: PASS"
