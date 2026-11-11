$ErrorActionPreference = "Stop"

Write-Host "[G6 PREPARE] Ensure secure PostgreSQL credential"
$envPath = ".env"
if (-not (Test-Path $envPath)) { Copy-Item ".env.example" $envPath }

$lines = Get-Content $envPath
$current = ($lines | Where-Object { $_ -match '^FATHER_POSTGRES_PASSWORD=' } | Select-Object -First 1)

if ([string]::IsNullOrWhiteSpace($current) -or $current -match '=(father|change-me-before-production)?$') {
    $newPassword = "Fth-" + [guid]::NewGuid().ToString("N") + "!"
    Write-Host "[INFO] Rotating PostgreSQL password for G6"
    docker compose exec -T postgres psql -U father -d father -c "ALTER USER father WITH PASSWORD '$newPassword';"
    if ($LASTEXITCODE -ne 0) { throw "Could not rotate PostgreSQL password" }

    $content = Get-Content $envPath -Raw
    if ($content -match '(?m)^FATHER_POSTGRES_PASSWORD=.*$') {
        $content = [regex]::Replace($content, '(?m)^FATHER_POSTGRES_PASSWORD=.*$', "FATHER_POSTGRES_PASSWORD=$newPassword")
    } else {
        $content += [Environment]::NewLine + "FATHER_POSTGRES_PASSWORD=$newPassword"
    }
    if ($content -match '(?m)^FATHER_POSTGRES_DB=.*$') {
        $content = [regex]::Replace($content, '(?m)^FATHER_POSTGRES_DB=.*$', 'FATHER_POSTGRES_DB=father')
    } else {
        $content += [Environment]::NewLine + 'FATHER_POSTGRES_DB=father'
    }
    if ($content -match '(?m)^FATHER_POSTGRES_USER=.*$') {
        $content = [regex]::Replace($content, '(?m)^FATHER_POSTGRES_USER=.*$', 'FATHER_POSTGRES_USER=father')
    } else {
        $content += [Environment]::NewLine + 'FATHER_POSTGRES_USER=father'
    }
    $dsn = "postgresql://father:$newPassword@postgres:5432/father"
    if ($content -match '(?m)^FATHER_POSTGRES_DSN=.*$') {
        $content = [regex]::Replace($content, '(?m)^FATHER_POSTGRES_DSN=.*$', "FATHER_POSTGRES_DSN=$dsn")
    } else {
        $content += [Environment]::NewLine + "FATHER_POSTGRES_DSN=$dsn"
    }
    Set-Content $envPath $content
} else {
    Write-Host "[PASS] PostgreSQL password already non-default"
}

Write-Host "[G6 PREPARE] Rebuild hardened runtime"
docker compose up -d --build --force-recreate
if ($LASTEXITCODE -ne 0) { throw "Hardened compose start failed" }
$deadline = (Get-Date).AddMinutes(3)
$ready = $false
do {
    try {
        $r = Invoke-RestMethod "http://localhost:8080/health/ready" -TimeoutSec 3
        if ($r.ready) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
} while ((Get-Date) -lt $deadline)
if (-not $ready) { docker compose ps; docker compose logs --tail=100 father-chassis; throw "Hardened FATHER did not become ready" }
Write-Host "G6 PREPARE: PASS"