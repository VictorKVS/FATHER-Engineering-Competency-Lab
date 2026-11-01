$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$SourceRoot = "F:\FATHER_MODELS\ollama"
$TargetRoot = "$env:USERPROFILE\.ollama\models"

if (-not (Test-Path $OllamaExe)) { throw "Ollama executable not found" }
if (-not (Test-Path $SourceRoot)) { throw "Source model store missing" }

Write-Host "=== FUA-001 OLLAMA STORE REPAIR ==="
Write-Host "SOURCE: $SourceRoot"
Write-Host "TARGET: $TargetRoot"

Write-Host ""
Write-Host "01. Stop Ollama"
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "02. Validate source manifests/blobs"
$sourceManifests = Join-Path $SourceRoot "manifests"
$sourceBlobs = Join-Path $SourceRoot "blobs"
if (-not (Test-Path $sourceManifests)) { throw "source manifests missing" }
if (-not (Test-Path $sourceBlobs)) { throw "source blobs missing" }

$missing = @()
$manifestFiles = Get-ChildItem $sourceManifests -Recurse -File
foreach ($m in $manifestFiles) {
    $j = Get-Content $m.FullName -Raw | ConvertFrom-Json
    $digests = @()
    if ($j.config.digest) { $digests += $j.config.digest }
    foreach ($layer in @($j.layers)) {
        if ($layer.digest) { $digests += $layer.digest }
    }
    foreach ($d in $digests) {
        $name = $d -replace ':','-'
        if (-not (Test-Path (Join-Path $sourceBlobs $name))) {
            $missing += "$($m.FullName) -> $name"
        }
    }
}
if ($missing.Count -gt 0) {
    Write-Host "MISSING BLOBS:"
    $missing | ForEach-Object { Write-Host $_ }
    throw "source store is incomplete"
}
Write-Host "SOURCE STORE INTEGRITY: PASS"

Write-Host ""
Write-Host "03. Ensure target directories"
$targetManifests = Join-Path $TargetRoot "manifests"
$targetBlobs = Join-Path $TargetRoot "blobs"
New-Item -ItemType Directory -Force -Path $targetManifests | Out-Null
New-Item -ItemType Directory -Force -Path $targetBlobs | Out-Null

Write-Host ""
Write-Host "04. Reconcile manifests without overwriting identical files"
$manifestCopied = 0
$manifestExisting = 0
$manifestConflicts = @()

foreach ($src in Get-ChildItem $sourceManifests -Recurse -File) {
    $relative = $src.FullName.Substring($sourceManifests.Length).TrimStart('\')
    $dest = Join-Path $targetManifests $relative
    $destDir = Split-Path -Parent $dest
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null

    if (Test-Path $dest) {
        $srcHash = (Get-FileHash $src.FullName -Algorithm SHA256).Hash
        $dstHash = (Get-FileHash $dest -Algorithm SHA256).Hash
        if ($srcHash -eq $dstHash) {
            $manifestExisting++
            continue
        }

        $manifestConflicts += "$relative source=$srcHash target=$dstHash"
        continue
    }

    Copy-Item $src.FullName $dest
    $manifestCopied++
}

Write-Host "MANIFEST EXISTING : $manifestExisting"
Write-Host "MANIFEST COPIED   : $manifestCopied"

if ($manifestConflicts.Count -gt 0) {
    Write-Host "MANIFEST CONFLICTS:"
    $manifestConflicts | ForEach-Object { Write-Host $_ }
    throw "target store contains conflicting manifests; refusing overwrite"
}

Write-Host ""
Write-Host "05. Materialize missing blobs into target store"
$copied = 0
$linked = 0
$existing = 0

foreach ($blob in Get-ChildItem $sourceBlobs -File) {
    $dest = Join-Path $targetBlobs $blob.Name
    if (Test-Path $dest) {
        $existing++
        continue
    }

    try {
        New-Item -ItemType HardLink -Path $dest -Target $blob.FullName -ErrorAction Stop | Out-Null
        $linked++
    } catch {
        Copy-Item $blob.FullName $dest -Force
        $copied++
    }
}

Write-Host "EXISTING BLOBS : $existing"
Write-Host "HARDLINKED     : $linked"
Write-Host "COPIED         : $copied"

Write-Host ""
Write-Host "06. Start default Ollama store"
Remove-Item Env:OLLAMA_MODELS -ErrorAction SilentlyContinue
$env:OLLAMA_HOST = "127.0.0.1:11434"

$Proc = Start-Process -FilePath $OllamaExe -ArgumentList "serve" -PassThru -WindowStyle Hidden

$ready = $false
for ($i=1; $i -le 40; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $tags = Invoke-RestMethod "http://127.0.0.1:11434/api/tags"
        $ready = $true
        break
    } catch {}
}
if (-not $ready) {
    if ($Proc -and -not $Proc.HasExited) { Stop-Process -Id $Proc.Id -Force }
    throw "Ollama failed to start after repair"
}

$modelCount = @($tags.models).Count
Write-Host "API MODELS      : $modelCount"
if ($modelCount -gt 0) {
    $tags.models | Select-Object name,size,modified_at | Format-Table -AutoSize
}

& $OllamaExe list
if ($LASTEXITCODE -ne 0) { throw "ollama list failed" }

if ($modelCount -eq 0) {
    Write-Host ""
    Write-Host "OLLAMA STORE REPAIR RESULT: BLOCKED - DEFAULT STORE STILL NOT INDEXED"
    exit 21
}

Write-Host ""
Write-Host "07. FUA discovery"
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
$TempPy = Join-Path $env:TEMP "fua-store-repair-check.py"

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

if ($Code -ne 0) { throw "FUA discovery failed after store repair" }

Write-Host ""
Write-Host "OLLAMA STORE REPAIR RESULT: PASS"
Write-Host "NOTE: Ollama remains running for real-model stage."
