$ErrorActionPreference = "Stop"

$images = @(
    "python:3.12-slim",
    "pgvector/pgvector:pg16",
    "redis:7-alpine"
)

foreach ($image in $images) {
    $success = $false
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        Write-Host "[INFO] Pulling $image (attempt $attempt/3)..."
        docker pull $image
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[PASS] Pulled $image"
            $success = $true
            break
        }
        Write-Host "[WARN] Pull failed for $image; retrying..."
        Start-Sleep -Seconds (5 * $attempt)
    }
    if (-not $success) {
        Write-Host "[FAIL] Could not pull $image after 3 attempts"
        exit 1
    }
}

Write-Host ""
Write-Host "DEPENDENCY PULL: PASS"