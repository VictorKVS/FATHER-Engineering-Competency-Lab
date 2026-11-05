$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER CODING ROLE BENCH MVP-08 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 82% -> target 86%" -ForegroundColor Yellow
python .\run_coding_role_bench_mvp08.py
if($LASTEXITCODE -ne 0){ throw "Coding Role Bench MVP-08 failed" }
Write-Host "=== CODING ROLE BENCH MVP-08: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 86%" -ForegroundColor Green
