$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER TEXT ANALYST EXAM v1 ===" -ForegroundColor Cyan
python ./build_text_analyst_exam.py
if($LASTEXITCODE -ne 0){ throw "Text Analyst Exam build failed" }
Write-Host "=== TEXT ANALYST EXAM v1: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence/text_analyst_exam/text_analyst_exam_v1.json"
