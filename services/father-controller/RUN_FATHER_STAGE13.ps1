$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.2 / STAGE 13 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage13.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Sandbox execution-boundary proof" -ForegroundColor Yellow
python run_stage13.py
if ($LASTEXITCODE -ne 0) { throw "Stage 13 failed" }

Write-Host "`n=== FATHER CHASSIS v2.2: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage13_evidence.json"
Write-Host "Audit: evidence\stage13_audit.jsonl"
