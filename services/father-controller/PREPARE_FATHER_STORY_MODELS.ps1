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

if(-not $env:OLLAMA_MODELS){
  $persisted=[Environment]::GetEnvironmentVariable("OLLAMA_MODELS","User")
  if($persisted){$env:OLLAMA_MODELS=$persisted}
}
if($env:OLLAMA_MODELS){Write-Host "OLLAMA_MODELS=$env:OLLAMA_MODELS" -ForegroundColor DarkGray}

if ($env:OLLAMA_MODELS) {
  $root = Split-Path $env:OLLAMA_MODELS -Qualifier
  if ($root) {
    try {
      $drive = Get-PSDrive ($root.TrimEnd(':')) -ErrorAction Stop
      Write-Host ("MODEL DRIVE {0}: free {1:N1} GB" -f $root, ($drive.Free/1GB)) -ForegroundColor DarkGray
    } catch {
      Write-Warning "Model drive is not ready: $root"
    }
  }
}

$required=@(
  "qwen2.5:7b",
  "ministral-3:8b"
)

$optional=@(
  "mistral-nemo"
)

function Has-Model([string]$m) {
  $list = & $ollama list 2>$null
  return ($list -match [regex]::Escape($m))
}

function Pull-WithRetry([string]$m, [int]$attempts=4) {
  for($i=1; $i -le $attempts; $i++) {
    Write-Host "PULL $m (attempt $i/$attempts)" -ForegroundColor Yellow
    & $ollama pull $m
    if($LASTEXITCODE -eq 0 -and (Has-Model $m)) {
      Write-Host "READY $m" -ForegroundColor Green
      return $true
    }
    if($i -lt $attempts) {
      $delay = 5 * $i
      Write-Warning "Pull failed for $m. Retrying in $delay sec..."
      Start-Sleep -Seconds $delay
    }
  }
  return $false
}

function Ensure-Model([string]$m, [bool]$requiredModel) {
  if (Has-Model $m) {
    Write-Host "PRESENT $m" -ForegroundColor Green
    return $true
  }

  $ok = Pull-WithRetry $m 4
  if($ok){ return $true }

  if ($requiredModel) {
    throw "Required Story model failed to pull after retries: $m"
  }

  Write-Warning "Optional Story model unavailable: $m. Story Bench will continue without it."
  return $false
}

foreach($m in $required) {
  [void](Ensure-Model $m $true)
}

$optionalReady=0
foreach($m in $optional) {
  if (Ensure-Model $m $false) { $optionalReady++ }
}

Write-Host ""
Write-Host "=== STORY CORE MODELS READY ===" -ForegroundColor Green
Write-Host "Required: qwen2.5:7b + ministral-3:8b" -ForegroundColor Green
if ($optionalReady -lt $optional.Count) {
  Write-Host "Optional mistral-nemo is not required for the first benchmark." -ForegroundColor Yellow
}
Write-Host "Next: ./RUN_FATHER_STORY_BENCH.ps1" -ForegroundColor Cyan
