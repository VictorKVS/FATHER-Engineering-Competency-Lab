$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.5 / STAGE 16 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage16.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Authenticated ledger checkpoint proof" -ForegroundColor Yellow
python run_stage16.py
if ($LASTEXITCODE -ne 0) { throw "Stage 16 failed" }

Write-Host "`n=== FATHER CHASSIS v2.5: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage16_evidence.json"
Write-Host "Checkpoint: evidence\stage16_checkpoint.json"
