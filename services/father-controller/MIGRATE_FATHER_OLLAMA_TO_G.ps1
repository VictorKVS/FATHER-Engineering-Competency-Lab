$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

$target="G:\FATHER_MODELS\ollama"
Write-Host "=== FATHER OLLAMA STORAGE MIGRATION ===" -ForegroundColor Cyan
Write-Host "TARGET: $target"

if(-not (Test-Path "G:\")){ throw "Drive G: is unavailable" }

New-Item -ItemType Directory -Force -Path $target | Out-Null

# Persist for current user and current shell.
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS",$target,"User")
$env:OLLAMA_MODELS=$target

Write-Host "OLLAMA_MODELS set to $target" -ForegroundColor Green

$ollama=(Get-Command ollama -ErrorAction SilentlyContinue).Source
if(-not $ollama){
  $fallback="$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
  if(Test-Path $fallback){$ollama=$fallback}
}
if(-not $ollama){throw "Ollama executable not found"}

# Restart Ollama so it picks up the new storage root.
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 5

Write-Host "Checking Ollama API..." -ForegroundColor Cyan
try {
  $v=Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/version" -TimeoutSec 10
  Write-Host ("Ollama API: "+$v.version) -ForegroundColor Green
} catch {
  throw ("Ollama API did not recover after storage migration: "+$_.Exception.Message)
}

Write-Host ""
Write-Host "New storage is empty unless models already exist there." -ForegroundColor Yellow
Write-Host "Next: .\PREPARE_FATHER_STORY_MODELS.ps1" -ForegroundColor Cyan
