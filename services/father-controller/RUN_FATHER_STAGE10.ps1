$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v1.9 / STAGE 10 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage10.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Agent Router proof" -ForegroundColor Yellow
python run_stage10.py
if ($LASTEXITCODE -ne 0) { throw "Stage 10 failed" }

Write-Host "`n=== FATHER CHASSIS v1.9: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage10_evidence.json"
