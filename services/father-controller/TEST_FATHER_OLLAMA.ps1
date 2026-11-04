param(
  [switch]$Recover
)
$ErrorActionPreference="Stop"

$ollama=(Get-Command ollama -ErrorAction SilentlyContinue).Source
if(-not $ollama){
  $fallback="$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
  if(Test-Path $fallback){$ollama=$fallback}
}
if(-not $ollama){throw "Ollama executable not found"}

function Test-OllamaApi {
  try {
    $v=Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/version" -TimeoutSec 5
    $t=Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 10
    return [PSCustomObject]@{
      Ok=$true
      Version=$v.version
      Models=@($t.models).Count
      Error=$null
    }
  } catch {
    return [PSCustomObject]@{
      Ok=$false
      Version=$null
      Models=0
      Error=$_.Exception.Message
    }
  }
}

Write-Host "=== FATHER OLLAMA PREFLIGHT ===" -ForegroundColor Cyan
& $ollama --version

$modelRoot=$env:OLLAMA_MODELS
if(-not $modelRoot -and (Test-Path "F:\FATHER_MODELS\ollama")) {
  $modelRoot="F:\FATHER_MODELS\ollama"
}
if($modelRoot){
  Write-Host "MODEL ROOT: $modelRoot"
  $qualifier=Split-Path $modelRoot -Qualifier
  if($qualifier){
    $driveName=$qualifier.TrimEnd(':')
    $drive=Get-PSDrive $driveName -ErrorAction SilentlyContinue
    if(-not $drive){
      throw "MODEL_STORAGE_NOT_READY: drive $qualifier is unavailable"
    }
    Write-Host ("MODEL DRIVE {0}: free {1:N1} GB" -f $qualifier,($drive.Free/1GB))
  }
  if(-not (Test-Path $modelRoot)){
    throw "MODEL_STORAGE_NOT_READY: path does not exist: $modelRoot"
  }
}

$health=Test-OllamaApi
if($health.Ok){
  Write-Host ("PASS Ollama API {0}; models={1}" -f $health.Version,$health.Models) -ForegroundColor Green
  exit 0
}

Write-Warning ("Ollama API unhealthy: "+$health.Error)
if(-not $Recover){
  Write-Host "Run: .\TEST_FATHER_OLLAMA.ps1 -Recover" -ForegroundColor Yellow
  exit 2
}

Write-Host "RECOVERY: restarting Ollama runtime..." -ForegroundColor Yellow
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

if($modelRoot){$env:OLLAMA_MODELS=$modelRoot}
Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 5

$health=Test-OllamaApi
if(-not $health.Ok){
  throw ("OLLAMA_RECOVERY_FAILED: "+$health.Error)
}

Write-Host ("RECOVERED Ollama API {0}; models={1}" -f $health.Version,$health.Models) -ForegroundColor Green
exit 0
