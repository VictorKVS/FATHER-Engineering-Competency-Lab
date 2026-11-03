$ErrorActionPreference = "Stop"
Write-Host "=== FATHER HYBRID RAG v3.2 / STAGE 23 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage23.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage23.py
if ($LASTEXITCODE -ne 0) { throw "Stage 23 failed" }
Write-Host "=== FATHER HYBRID RAG v3.2: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage23_evidence.json"
