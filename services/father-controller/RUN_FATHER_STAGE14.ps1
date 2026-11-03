$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.3 / STAGE 14 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage14.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Evidence + Provenance integrity proof" -ForegroundColor Yellow
python run_stage14.py
if ($LASTEXITCODE -ne 0) { throw "Stage 14 failed" }

Write-Host "`n=== FATHER CHASSIS v2.3: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage14_evidence.json"
Write-Host "Provenance: evidence\stage14_provenance.json"
Write-Host "Audit: evidence\stage14_audit.jsonl"
