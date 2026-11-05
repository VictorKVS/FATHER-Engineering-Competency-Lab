$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER HYBRID RUNTIME ROUTER MVP-03 ===" -ForegroundColor Cyan
python .\run_hybrid_runtime_router_mvp03.py
if($LASTEXITCODE -ne 0){ throw "Hybrid Runtime Router MVP-03 failed" }
Write-Host "=== HYBRID RUNTIME ROUTER MVP-03: PASS ===" -ForegroundColor Green
