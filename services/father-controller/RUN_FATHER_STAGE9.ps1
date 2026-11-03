$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v1.8 / STAGE 9 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage9.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Agent Zoo registry + multi-agent proof" -ForegroundColor Yellow
python run_stage9.py
if ($LASTEXITCODE -ne 0) { throw "Stage 9 failed" }

Write-Host "`n=== FATHER CHASSIS v1.8: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage9_evidence.json"
