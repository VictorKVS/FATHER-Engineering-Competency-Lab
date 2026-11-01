$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$ModelRoot = "F:\FATHER_MODELS\ollama"

if (-not (Test-Path $OllamaExe)) {
    throw "Ollama executable not found: $OllamaExe"
}
if (-not (Test-Path $ModelRoot)) {
    throw "Ollama model root not found: $ModelRoot"
}

Write-Host "=== FUA-001 OLLAMA MODEL-STORE REBIND ==="
Write-Host "OLLAMA EXE   : $OllamaExe"
Write-Host "MODEL ROOT   : $ModelRoot"

Write-Host ""
Write-Host "01. Validate model-store structure"
$ManifestRoot = Join-Path $ModelRoot "manifests"
$BlobRoot = Join-Path $ModelRoot "blobs"

if (-not (Test-Path $ManifestRoot)) { throw "manifest root missing: $ManifestRoot" }
if (-not (Test-Path $BlobRoot)) {
    Write-Host "BLOBS ROOT   : MISSING"
} else {
    $blobCount = (Get-ChildItem $BlobRoot -File -ErrorAction SilentlyContinue | Measure-Object).Count
    $blobBytes = (Get-ChildItem $BlobRoot -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $blobBytes) { $blobBytes = 0 }
    Write-Host "BLOBS COUNT  : $blobCount"
    Write-Host "BLOBS BYTES  : $blobBytes"
}

$manifestFiles = Get-ChildItem $ManifestRoot -Recurse -File -ErrorAction Stop
Write-Host "MANIFESTS    : $($manifestFiles.Count)"
$manifestFiles | Select-Object -First 20 FullName, Length | Format-Table -AutoSize

Write-Host ""
Write-Host "02. Stop existing Ollama processes"
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "03. Start Ollama with explicit model root"
$env:OLLAMA_MODELS = $ModelRoot
$env:OLLAMA_HOST = "127.0.0.1:11434"

$Proc = Start-Process -FilePath $OllamaExe -ArgumentList "serve" -PassThru -WindowStyle Hidden

$ready = $false
for ($i = 1; $i -le 40; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $r = Invoke-RestMethod "http://127.0.0.1:11434/api/tags"
        $ready = $true
        break
    } catch {}
}

if (-not $ready) {
    if ($Proc -and -not $Proc.HasExited) { Stop-Process -Id $Proc.Id -Force }
    throw "Ollama did not become ready on 127.0.0.1:11434"
}

Write-Host "OLLAMA READY : PASS"

Write-Host ""
Write-Host "04. API model inventory"
$tags = Invoke-RestMethod "http://127.0.0.1:11434/api/tags"
$modelCount = @($tags.models).Count
Write-Host "API MODELS   : $modelCount"
if ($modelCount -gt 0) {
    $tags.models | Select-Object name, size, modified_at | Format-Table -AutoSize
}

Write-Host ""
Write-Host "05. Ollama CLI inventory"
& $OllamaExe list
$cliCode = $LASTEXITCODE
if ($cliCode -ne 0) { throw "ollama list failed with exit code $cliCode" }

if ($modelCount -eq 0) {
    Write-Host ""
    Write-Host "REBIND RESULT: STORE_VISIBLE_BUT_NO_MODELS"
    if ($Proc -and -not $Proc.HasExited) { Stop-Process -Id $Proc.Id -Force }
    exit 21
}

Write-Host ""
Write-Host "06. FUA discovery"
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
$TempPy = Join-Path $env:TEMP "fua-after-rebind.py"
@'
from father_fua.local_models import discover_local_models
models=discover_local_models()
print("FUA_DISCOVERED={}".format(len(models)))
for m in models:
    print("{}|{}|{}".format(m.transport,m.model_id,m.base_url))
if not models:
    raise SystemExit(22)
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy
    $Code = $LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) {
    if ($Proc -and -not $Proc.HasExited) { Stop-Process -Id $Proc.Id -Force }
    throw "FUA discovery failed after Ollama rebind"
}

Write-Host ""
Write-Host "OLLAMA MODEL-STORE REBIND RESULT: PASS"
Write-Host "NOTE: Ollama serve process remains running for the next real-model stage."
