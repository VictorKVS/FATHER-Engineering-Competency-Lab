$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.0 / STAGE 11 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage11.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Workflow + State + Audit proof" -ForegroundColor Yellow
python run_stage11.py
if ($LASTEXITCODE -ne 0) { throw "Stage 11 failed" }

Write-Host "`n=== FATHER CHASSIS v2.0: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage11_evidence.json"
Write-Host "Audit: evidence\stage11_audit.jsonl"
