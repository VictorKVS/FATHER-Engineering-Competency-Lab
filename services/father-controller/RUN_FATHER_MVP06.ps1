$ErrorActionPreference = "Stop"
Write-Host "=== FATHER FACTORY MVP-06 / PRIMITIVE RELEASE LINE ===" -ForegroundColor Cyan
python --version
python -m compileall father run_factory_mvp06.py
if ($LASTEXITCODE -ne 0) { throw "MVP-06 syntax check failed" }
python .\run_factory_mvp06.py
if ($LASTEXITCODE -ne 0) { throw "Factory MVP-06 failed" }
Write-Host "=== FATHER FACTORY MVP-06: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\factory_mvp06_release_line.json"
Write-Host "Release: releases\father-auto-general-rag-v1-mvp06"
