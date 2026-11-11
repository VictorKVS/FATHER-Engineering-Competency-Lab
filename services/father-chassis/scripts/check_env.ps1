$ErrorActionPreference = "Stop"

function Check-Command($name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        Write-Host "[FAIL] $name not found"
        return $false
    }
    Write-Host "[PASS] $name -> $($cmd.Source)"
    return $true
}

$ok = $true
$ok = (Check-Command "git") -and $ok
$ok = (Check-Command "docker") -and $ok
$ok = (Check-Command "python") -and $ok

if (Get-Command docker -ErrorAction SilentlyContinue) {
    try { docker version | Out-Null; Write-Host "[PASS] Docker Engine reachable" }
    catch { Write-Host "[FAIL] Docker Engine unavailable"; $ok = $false }

    try { docker compose version | Out-Null; Write-Host "[PASS] Docker Compose available" }
    catch { Write-Host "[FAIL] Docker Compose unavailable"; $ok = $false }
}

if ($ok) { Write-Host "`nENVIRONMENT CHECK: PASS"; exit 0 }
Write-Host "`nENVIRONMENT CHECK: FAIL"
exit 1
