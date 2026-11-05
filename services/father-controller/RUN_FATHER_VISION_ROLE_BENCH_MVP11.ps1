$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER VISION ROLE BENCH MVP-11 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 93% -> target 96%" -ForegroundColor Yellow
python .\run_vision_role_bench_mvp11.py
if($LASTEXITCODE -ne 0){ throw "Vision Role Bench MVP-11 failed" }
Write-Host "=== VISION ROLE BENCH MVP-11: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 96%" -ForegroundColor Green
