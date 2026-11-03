$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v1.6 / STAGE 7 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage7.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Minimal chassis end-to-end proof" -ForegroundColor Yellow
python run_stage7.py
if ($LASTEXITCODE -ne 0) { throw "Stage 7 failed" }

Write-Host "`n=== FATHER CHASSIS v1.6: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage7_evidence.json"
Write-Host "File output: evidence\stage7_file_output.json"
