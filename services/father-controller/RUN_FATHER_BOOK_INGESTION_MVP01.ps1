$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

Write-Host "=== FATHER BOOK INGESTION MVP-01 ===" -ForegroundColor Cyan

$inputDir = Join-Path $PSScriptRoot "book_benchmark/input"
New-Item -ItemType Directory -Force -Path $inputDir | Out-Null

try {
    python -c "import pypdf" 2>$null
    if($LASTEXITCODE -ne 0){ throw "missing" }
} catch {
    Write-Host "Installing pypdf for PDF text extraction..." -ForegroundColor Yellow
    python -m pip install pypdf
    if($LASTEXITCODE -ne 0){ throw "Could not install pypdf" }
}

python ./run_book_ingestion_mvp01.py
if($LASTEXITCODE -ne 0){
    throw "Book Ingestion MVP-01 did not fully pass. See evidence/book_ingestion/extraction_report.json"
}

Write-Host "=== BOOK INGESTION MVP-01: PASS ===" -ForegroundColor Green
Write-Host "Evidence: evidence/book_ingestion/" -ForegroundColor Green
