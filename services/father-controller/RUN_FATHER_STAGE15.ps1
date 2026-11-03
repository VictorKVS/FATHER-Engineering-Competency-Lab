$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.4 / STAGE 15 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage15.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Append-only Evidence Ledger proof" -ForegroundColor Yellow
python run_stage15.py
if ($LASTEXITCODE -ne 0) { throw "Stage 15 failed" }

Write-Host "`n=== FATHER CHASSIS v2.4: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage15_evidence.json"
Write-Host "Ledger: evidence\stage15_ledger.jsonl"
Write-Host "Audit: evidence\stage15_audit.jsonl"
