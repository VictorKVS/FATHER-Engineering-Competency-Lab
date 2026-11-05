$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER ROLE MODEL MATRIX MVP-01 ===" -ForegroundColor Cyan
python .\run_role_model_matrix_mvp01.py
if($LASTEXITCODE -ne 0){ throw "Role Model Matrix MVP-01 failed" }
Write-Host "=== ROLE MODEL MATRIX MVP-01: PASS ===" -ForegroundColor Green
