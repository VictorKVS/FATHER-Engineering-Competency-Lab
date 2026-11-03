$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.7 / STAGE 18 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage18.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] GitHub external-anchor proof" -ForegroundColor Yellow
python run_stage18.py
if ($LASTEXITCODE -ne 0) { throw "Stage 18 failed" }

Write-Host "`n=== FATHER CHASSIS v2.7: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage18_evidence.json"
