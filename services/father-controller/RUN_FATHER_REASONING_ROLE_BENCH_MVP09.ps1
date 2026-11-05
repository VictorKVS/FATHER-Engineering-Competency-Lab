$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER REASONING ROLE BENCH MVP-09 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 85% -> target 89%" -ForegroundColor Yellow
python .\run_reasoning_role_bench_mvp09.py
if($LASTEXITCODE -ne 0){ throw "Reasoning Role Bench MVP-09 failed" }
Write-Host "=== REASONING ROLE BENCH MVP-09: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 89%" -ForegroundColor Green
