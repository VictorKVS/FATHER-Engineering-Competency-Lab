$ErrorActionPreference = "Stop"
Write-Host "=== FATHER UNIFIED AGENT v3.1 / STAGE 22 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage22.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage22.py
if ($LASTEXITCODE -ne 0) { throw "Stage 22 failed" }
Write-Host "=== FATHER UNIFIED AGENT v3.1: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage22_evidence.json"
