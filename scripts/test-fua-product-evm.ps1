$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 PRODUCT TEST EVM ==="

Write-Host ""
Write-Host "01. Product-level pytest"
& $Py -m pytest tests/test_product_fua001.py -q
if ($LASTEXITCODE -ne 0) {
    throw "product test failed"
}
Write-Host "PRODUCT PYTEST   : PASS"

Write-Host ""
Write-Host "02. Full reliability gate"
& (Join-Path $PSScriptRoot "test-fua-reliability-gate-evm.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "reliability gate failed during product test"
}
Write-Host "RELIABILITY GATE : PASS"

Write-Host ""
Write-Host "03. Sandbox stress"
& (Join-Path $PSScriptRoot "test-fua-sandbox-stress-evm.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "sandbox stress failed during product test"
}
Write-Host "SANDBOX STRESS   : PASS"

Write-Host ""
Write-Host "04. Fault/recovery stress"
& (Join-Path $PSScriptRoot "test-fua-fault-recovery-stress-evm.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "fault/recovery stress failed during product test"
}
Write-Host "FAULT/RECOVERY   : PASS"

Write-Host ""
Write-Host "FUA-001 PRODUCT TEST RESULT: PASS"
