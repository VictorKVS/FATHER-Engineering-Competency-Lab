$ErrorActionPreference = "Stop"
Write-Host "=== FATHER HYBRID BRAIN LAB / STAGE 25 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage25.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage25.py
if ($LASTEXITCODE -ne 0) { throw "Stage 25 failed" }
Write-Host "=== FATHER HYBRID BRAIN LAB: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage25_hybrid_brain_lab.json"
