$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

New-Item -ItemType Directory -Path ".\data" -Force | Out-Null
New-Item -ItemType Directory -Path ".\evidence" -Force | Out-Null

Write-Host "=== FATHER CHASSIS v1.5 / STAGE 6 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage6.py | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Knowledge Slot + Competency Pack proof" -ForegroundColor Yellow
python run_stage6.py
if ($LASTEXITCODE -ne 0) { throw "Stage 6 failed" }

Write-Host "`n=== FATHER CHASSIS v1.5: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage6_evidence.json"
Write-Host "Database: data\model_zoo.db"
