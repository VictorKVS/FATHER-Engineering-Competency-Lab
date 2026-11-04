$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER STORY MODEL BENCH ===" -ForegroundColor Cyan
python .\run_story_model_bench.py
if($LASTEXITCODE -ne 0){throw "Story model bench failed"}
Write-Host "Report: evidence\story_model_bench_latest.json" -ForegroundColor Green
