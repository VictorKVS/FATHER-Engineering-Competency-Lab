$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

Write-Host "=== FUA-001 LOCAL MODEL BOOTSTRAP ==="

function Test-Port {
    param([int]$Port)
    return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
}

Write-Host ""
Write-Host "01. Detect installed runtimes"

$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
$ollamaExe = $null
if ($ollamaCmd) {
    $ollamaExe = $ollamaCmd.Source
    Write-Host "OLLAMA CLI      : $ollamaExe"
} else {
    $candidate = @(
        "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
        "$env:ProgramFiles\Ollama\ollama.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($candidate) {
        $ollamaExe = $candidate
        Write-Host "OLLAMA EXE      : $ollamaExe"
    } else {
        Write-Host "OLLAMA          : NOT FOUND"
    }
}

$lmStudioCandidates = @(
    "$env:LOCALAPPDATA\Programs\LM Studio\LM Studio.exe",
    "$env:LOCALAPPDATA\LM Studio\LM Studio.exe"
)
$lmStudio = $lmStudioCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($lmStudio) {
    Write-Host "LM STUDIO       : $lmStudio"
} else {
    Write-Host "LM STUDIO       : NOT FOUND"
}

Write-Host ""
Write-Host "02. Detect running endpoints"
foreach ($port in 11434,8000,1234,8080) {
    if (Test-Port $port) {
        Write-Host "PORT $port       : LISTEN"
    } else {
        Write-Host "PORT $port       : CLOSED"
    }
}

Write-Host ""
Write-Host "03. Start Ollama service when installed but inactive"
$StartedOllama = $false
if ($ollamaExe -and -not (Test-Port 11434)) {
    Write-Host "Starting Ollama serve..."
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    for ($i=1; $i -le 40; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-Port 11434) {
            $StartedOllama = $true
            break
        }
    }
}

if (Test-Port 11434) {
    Write-Host "OLLAMA SERVICE  : RUNNING"
} elseif ($ollamaExe) {
    Write-Host "OLLAMA SERVICE  : FAILED TO START"
}

Write-Host ""
Write-Host "04. Discover models through FUA"
$TempPy = Join-Path $env:TEMP "fua-model-bootstrap-check.py"
@'
from father_fua.local_models import discover_local_models
models=discover_local_models()
print("DISCOVERED_MODELS={}".format(len(models)))
for m in models:
    print("{}|{}|{}".format(m.transport,m.model_id,m.base_url))
if not models:
    raise SystemExit(20)
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code = $LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -eq 0) {
    Write-Host ""
    Write-Host "LOCAL MODEL BOOTSTRAP RESULT: SERVICE_AND_MODEL_READY"
    exit 0
}

Write-Host ""
Write-Host "05. Scan candidate model stores"
$roots = @(
    'F:\FATHER_MODELS',
    'F:\FATHER_MODELS\ollama',
    "$env:USERPROFILE\.ollama\models",
    "$env:LOCALAPPDATA\LM Studio\models",
    'G:\1'
)

$found = @()
foreach ($root in $roots) {
    if (Test-Path $root) {
        Write-Host "ROOT: $root"
        $items = Get-ChildItem $root -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Extension -in '.gguf','.safetensors' -or
                $_.FullName -match '\\manifests\\'
            } |
            Select-Object -First 50 FullName, Length
        if ($items) {
            $found += $items
            $items | Format-Table -AutoSize
        } else {
            Write-Host "  no candidate model artifacts found in bounded scan"
        }
    }
}

Write-Host ""
if ($found.Count -gt 0) {
    Write-Host "LOCAL MODEL BOOTSTRAP RESULT: MODEL_ARTIFACTS_FOUND_BUT_NOT_SERVED"
    exit 21
}

if ($ollamaExe -or $lmStudio) {
    Write-Host "LOCAL MODEL BOOTSTRAP RESULT: RUNTIME_FOUND_NO_SERVED_MODEL"
    exit 22
}

Write-Host "LOCAL MODEL BOOTSTRAP RESULT: NO_RUNTIME_NO_MODEL_FOUND"
exit 23
