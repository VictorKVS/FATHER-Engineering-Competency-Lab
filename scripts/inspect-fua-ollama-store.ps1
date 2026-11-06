$ErrorActionPreference = "Stop"

$ModelRoot = "F:\FATHER_MODELS\ollama"
$ManifestRoot = Join-Path $ModelRoot "manifests"
$BlobRoot = Join-Path $ModelRoot "blobs"

Write-Host "=== FUA-001 OLLAMA STORE INSPECT ==="
Write-Host "MODEL ROOT: $ModelRoot"

$manifests = Get-ChildItem $ManifestRoot -Recurse -File -ErrorAction Stop
Write-Host "MANIFEST COUNT: $($manifests.Count)"
Write-Host ""

foreach ($m in $manifests) {
    Write-Host "=== MANIFEST: $($m.FullName) ==="
    $raw = Get-Content $m.FullName -Raw
    Write-Host $raw

    try {
        $j = $raw | ConvertFrom-Json
        $digests = @()
        if ($j.config.digest) { $digests += $j.config.digest }
        if ($j.layers) {
            foreach ($layer in $j.layers) {
                if ($layer.digest) { $digests += $layer.digest }
            }
        }
        foreach ($d in $digests) {
            $name = $d -replace ':','-'
            $blob = Join-Path $BlobRoot $name
            if (Test-Path $blob) {
                $item = Get-Item $blob
                Write-Host "BLOB OK      : $name  $($item.Length)"
            } else {
                Write-Host "BLOB MISSING : $name"
            }
        }
    } catch {
        Write-Host "MANIFEST JSON PARSE FAILED: $($_.Exception.Message)"
    }
    Write-Host ""
}

Write-Host "=== STORE DIRECTORY ATTRIBUTES ==="
Get-Item $ModelRoot | Select-Object FullName, Attributes, LinkType, Target | Format-List
Get-Item $ManifestRoot | Select-Object FullName, Attributes, LinkType, Target | Format-List
Get-Item $BlobRoot | Select-Object FullName, Attributes, LinkType, Target | Format-List

Write-Host "OLLAMA STORE INSPECT RESULT: COMPLETE"
