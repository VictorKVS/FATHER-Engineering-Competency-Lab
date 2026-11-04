$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER NARRATIVE KB MVP-01 ===" -ForegroundColor Cyan
python .\run_narrative_demo_mvp01.py
if($LASTEXITCODE -ne 0){throw "Narrative KB MVP-01 failed"}
Write-Host "=== NARRATIVE KB MVP-01: PASS ===" -ForegroundColor Green
