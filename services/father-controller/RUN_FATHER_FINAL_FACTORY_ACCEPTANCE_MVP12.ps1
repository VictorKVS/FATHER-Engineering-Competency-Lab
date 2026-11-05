$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER FINAL FACTORY ACCEPTANCE MVP-12 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 96% -> target 100%" -ForegroundColor Yellow
python .\run_final_factory_acceptance_mvp12.py
if($LASTEXITCODE -ne 0){ throw "Final Factory Acceptance MVP-12 failed" }
Write-Host "=== FINAL FACTORY ACCEPTANCE MVP-12: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 100%" -ForegroundColor Green
Write-Host "FATHER FACTORY CORE: READY" -ForegroundColor Green
