$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

$ollama=(Get-Command ollama -ErrorAction SilentlyContinue).Source
if (-not $ollama) {
  $fallback="$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
  if (Test-Path $fallback) { $ollama=$fallback }
}
if (-not $ollama) { throw "Ollama executable not found" }

Write-Host "=== FATHER STORY MODEL PREPARE ===" -ForegroundColor Cyan
& $ollama --version

$models=@(
  "qwen2.5:7b",
  "ministral-3:8b",
  "mistral-nemo"
)

$current=& $ollama list
foreach($m in $models){
  if($current -match [regex]::Escape(($m -split ':')[0])){
    Write-Host "PRESENT $m" -ForegroundColor Green
  } else {
    Write-Host "PULL $m" -ForegroundColor Yellow
    & $ollama pull $m
    if($LASTEXITCODE -ne 0){ throw "Failed to pull $m" }
  }
}
Write-Host "=== STORY MODELS READY ===" -ForegroundColor Green
