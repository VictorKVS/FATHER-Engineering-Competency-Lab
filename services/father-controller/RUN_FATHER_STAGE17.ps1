$ErrorActionPreference = "Stop"

Write-Host "=== FATHER CHASSIS v2.6 / STAGE 17 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage17.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] External anchor artifact proof" -ForegroundColor Yellow
python run_stage17.py
if ($LASTEXITCODE -ne 0) { throw "Stage 17 failed" }

Write-Host "`n=== FATHER CHASSIS v2.6: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage17_evidence.json"
Write-Host "Anchor: evidence\stage17_anchor.json"
