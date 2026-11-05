$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER CREATIVE ROLE BENCH MVP-10 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 89% -> target 93%" -ForegroundColor Yellow
python .\run_creative_role_bench_mvp10.py
if($LASTEXITCODE -ne 0){ throw "Creative Role Bench MVP-10 failed" }
Write-Host "=== CREATIVE ROLE BENCH MVP-10: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 93%" -ForegroundColor Green
