$ErrorActionPreference = "Stop"
Write-Host "=== FATHER BRAIN EXPERIMENTS / STAGE 24 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage24.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage24.py
if ($LASTEXITCODE -ne 0) { throw "Stage 24 failed" }
Write-Host "=== FATHER BRAIN EXPERIMENTS: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage24_brain_experiments.json"
