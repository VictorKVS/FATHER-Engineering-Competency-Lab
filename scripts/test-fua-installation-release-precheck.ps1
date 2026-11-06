$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 INSTALLATION / RELEASE PRECHECK ==="

$ManifestPath = Join-Path $Repo "factory\chassis\FUA-001\manifest.json"
$Manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

Write-Host ("MANIFEST STATUS  : {0}" -f $Manifest.status)
Write-Host ("INSTALL PERMIT   : {0}" -f $Manifest.installation_permit)
Write-Host ("PRODUCTION READY : {0}" -f $Manifest.production_ready)
Write-Host ("NEXT GATES       : {0}" -f (($Manifest.next_factory_gates) -join ", "))

Write-Host ""
Write-Host "01. Release-gate regression tests"
& $Py -m pytest tests/test_human_acceptance.py tests/test_installation_gate.py -q
if ($LASTEXITCODE -ne 0) {
    throw "release-gate regression tests failed"
}
Write-Host "RELEASE TESTS    : PASS"

Write-Host ""
Write-Host "02. Evidence audit"
& (Join-Path $PSScriptRoot "test-fua-final-evidence-audit.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "evidence audit failed"
}
Write-Host "EVIDENCE AUDIT   : PASS"

Write-Host ""
Write-Host "03. Human acceptance state"
if (($Manifest.next_factory_gates) -contains "HUMAN_ACCEPTANCE") {
    Write-Host "HUMAN ACCEPTANCE: PENDING"
} else {
    Write-Host "HUMAN ACCEPTANCE: STATE_CHANGED"
}

if ($Manifest.installation_permit -ne "DENIED") {
    throw "precheck expects permit DENIED until acceptance is applied"
}
if ($Manifest.production_ready -ne $false) {
    throw "precheck expects production_ready=false until release completion"
}

Write-Host ""
Write-Host "INSTALLATION / RELEASE PRECHECK RESULT: PASS"
Write-Host "RELEASE DECISION                         : BLOCKED_PENDING_HUMAN_ACCEPTANCE"
