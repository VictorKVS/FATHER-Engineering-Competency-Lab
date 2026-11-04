$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

$ollama=(Get-Command ollama -ErrorAction SilentlyContinue).Source
if(-not $ollama){
  $fallback="$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
  if(Test-Path $fallback){$ollama=$fallback}
}
if(-not $ollama){throw "Ollama executable not found"}

if(-not $env:OLLAMA_MODELS){
  $persisted=[Environment]::GetEnvironmentVariable("OLLAMA_MODELS","User")
  if($persisted){$env:OLLAMA_MODELS=$persisted}
}
if(-not $env:OLLAMA_MODELS){$env:OLLAMA_MODELS="G:\FATHER_MODELS\ollama"}

Write-Host "=== FATHER CORE MODEL RESTORE ===" -ForegroundColor Cyan
Write-Host "OLLAMA_MODELS=$env:OLLAMA_MODELS"
& $ollama --version

$required=@(
  "llama3.2:1b",
  "qwen2.5:7b",
  "qwen2.5-coder:7b-instruct-q4_K_M",
  "deepseek-r1:7b"
)

function Has-Model([string]$m){
  $list=& $ollama list 2>$null
  return ($list -match [regex]::Escape($m))
}

foreach($m in $required){
  if(Has-Model $m){
    Write-Host "PRESENT $m" -ForegroundColor Green
    continue
  }
  Write-Host "PULL $m" -ForegroundColor Yellow
  & $ollama pull $m
  if($LASTEXITCODE -ne 0){throw "Failed to pull required FATHER model: $m"}
  if(-not (Has-Model $m)){throw "Model still missing after pull: $m"}
  Write-Host "READY $m" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== FATHER CORE MODELS READY ===" -ForegroundColor Green
& $ollama list
Write-Host "Next: ./RUN_FATHER_STAGE29.ps1" -ForegroundColor Cyan
