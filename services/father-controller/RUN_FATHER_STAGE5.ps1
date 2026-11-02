$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

New-Item -ItemType Directory -Path ".\data" -Force | Out-Null
New-Item -ItemType Directory -Path ".\evidence" -Force | Out-Null

Write-Host "=== FATHER CHASSIS v1.4 / STAGE 5 ===" -ForegroundColor Cyan
python --version

Write-Host "`n[1/2] Syntax check" -ForegroundColor Yellow
python -m compileall father run_stage5.py | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Syntax check failed" }

Write-Host "`n[2/2] Deterministic quality benchmark" -ForegroundColor Yellow
python run_stage5.py
if ($LASTEXITCODE -ne 0) { throw "Stage 5 failed" }

Write-Host "`n=== FATHER CHASSIS v1.4: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence\stage5_evidence.json"
Write-Host "Database: data\model_zoo.db"
