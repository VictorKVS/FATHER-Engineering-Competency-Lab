$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER ADAPTIVE ROLE ROUTER MVP-02 / SHADOW MODE ===" -ForegroundColor Cyan
python .\run_adaptive_role_router_mvp02.py
if($LASTEXITCODE -ne 0){ throw "Adaptive Role Router MVP-02 failed" }
Write-Host "=== ADAPTIVE ROLE ROUTER MVP-02: PASS ===" -ForegroundColor Green
