$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
Write-Host "=== FATHER TEXT ANALYST QUALIFICATION BENCH MVP-01 ===" -ForegroundColor Cyan

& "$PSScriptRoot\..\..\TEST_FATHER_OLLAMA.ps1"
if($LASTEXITCODE -ne 0){ throw "Ollama preflight failed" }

if(-not (Test-Path ".\evidence\book_ingestion\chunks.jsonl")){
  throw "Missing evidence/book_ingestion/chunks.jsonl. Run Book Ingestion MVP-01 first."
}
if(-not (Test-Path ".\evidence\text_analyst_exam\text_analyst_exam_v1.json")){
  throw "Missing Text Analyst Exam. Run RUN_FATHER_TEXT_ANALYST_EXAM_BUILD.ps1 first."
}

python .\run_text_analyst_qualification.py --questions 30 --top-k 6 --timeout 180
if($LASTEXITCODE -ne 0){ throw "Qualification bench failed" }

Write-Host "=== QUALIFICATION BENCH COMPLETE ===" -ForegroundColor Green
Write-Host "Evidence: evidence/text_analyst_qualification/" -ForegroundColor Green
