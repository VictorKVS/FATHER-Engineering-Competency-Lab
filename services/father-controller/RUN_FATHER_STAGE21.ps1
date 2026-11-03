$ErrorActionPreference = "Stop"
Write-Host "=== FATHER CHASSIS v3.0 / STAGE 21 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage21.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage21.py
if ($LASTEXITCODE -ne 0) { throw "Stage 21 failed" }
Write-Host "=== FATHER CHASSIS v3.0: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage21_evidence.json"
