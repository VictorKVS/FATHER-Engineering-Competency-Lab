$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 PILOT TEST EVM ==="

Write-Host ""
Write-Host "01. Pilot mission suite"
& $Py -m pytest tests/test_pilot_fua001.py -q
if ($LASTEXITCODE -ne 0) {
    throw "pilot mission suite failed"
}
Write-Host "PILOT MISSIONS   : PASS"

Write-Host ""
Write-Host "02. Product regression"
& (Join-Path $PSScriptRoot "test-fua-product-evm.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "product regression failed during pilot"
}
Write-Host "PRODUCT REGRESSION: PASS"

Write-Host ""
Write-Host "03. Release state"
$Manifest = Get-Content (Join-Path $Repo "factory\chassis\FUA-001\manifest.json") -Raw | ConvertFrom-Json
Write-Host ("STATUS           : {0}" -f $Manifest.status)
Write-Host ("INSTALL PERMIT   : {0}" -f $Manifest.installation_permit)
Write-Host ("PRODUCTION READY : {0}" -f $Manifest.production_ready)

if ($Manifest.installation_permit -ne "PASS") {
    throw "pilot requires installation permit PASS"
}
if ($Manifest.production_ready -ne $false) {
    throw "pilot requires production_ready=false"
}

Write-Host ""
Write-Host "FUA-001 PILOT TEST RESULT: PASS"
