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

if ($env:OLLAMA_MODELS) {
  Write-Host "OLLAMA_MODELS=$env:OLLAMA_MODELS" -ForegroundColor DarkGray
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
  return ($list -match [regex]::Escape($m)) -or ($list -match [regex]::Escape(($m -split ':')[0]))
}

function Ensure-Model([string]$m, [bool]$requiredModel) {
  if (Has-Model $m) {
    Write-Host "PRESENT $m" -ForegroundColor Green
    return $true
  }

  Write-Host "PULL $m" -ForegroundColor Yellow
  & $ollama pull $m

  if ($LASTEXITCODE -eq 0 -and (Has-Model $m)) {
    Write-Host "READY $m" -ForegroundColor Green
    return $true
  }

  if ($requiredModel) {
    throw "Required Story model failed to pull: $m"
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
  Write-Host "You can retry it later after the model drive is stable." -ForegroundColor Yellow
}
Write-Host "Next: .\RUN_FATHER_STORY_BENCH.ps1" -ForegroundColor Cyan
