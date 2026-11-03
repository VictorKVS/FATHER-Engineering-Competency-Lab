$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.1 / STAGE 12 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage12.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Policy / UAG gate proof" -ForegroundColor Yellow
python run_stage12.py
if ($LASTEXITCODE -ne 0) { throw "Stage 12 failed" }

Write-Host "`n=== FATHER CHASSIS v2.1: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage12_evidence.json"
Write-Host "Audit: evidence\stage12_audit.jsonl"
