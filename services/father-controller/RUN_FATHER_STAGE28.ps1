$ErrorActionPreference = "Stop"
Write-Host "=== FATHER MODEL KNOWLEDGE BASE / STAGE 28 ===" -ForegroundColor Cyan
python --version
python -m compileall father run_stage28.py
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }
python .\run_stage28.py
if ($LASTEXITCODE -ne 0) { throw "Stage 28 failed" }
Write-Host "=== FATHER MODEL KNOWLEDGE BASE: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage28_model_knowledge_base.json"
