param(
  [string]$JudgeModel = "qwen2.5:7b",
  [int]$QuestionsPerBook = 12
)
$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER TEXT ANALYST QUALITY JUDGE MVP-01 ===" -ForegroundColor Cyan

if(-not (Test-Path ".\evidence\text_analyst_qualification\qualification_latest.json")){
  throw "Missing qualification_latest.json"
}

python .\run_text_analyst_quality_judge.py --judge-model $JudgeModel --questions-per-book $QuestionsPerBook
if($LASTEXITCODE -ne 0){ throw "Quality judge failed" }

Write-Host "=== QUALITY JUDGE COMPLETE ===" -ForegroundColor Green
Write-Host "Evidence: evidence/text_analyst_quality/quality_latest.json" -ForegroundColor Green
