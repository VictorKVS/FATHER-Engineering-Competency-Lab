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

function Check-NativeCommand($label, [scriptblock]$command) {
    & $command
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] $label"
        return $false
    }
    Write-Host "[PASS] $label"
    return $true
}

$ok = $true
$ok = (Check-Command "git") -and $ok
$ok = (Check-Command "docker") -and $ok
$ok = (Check-Command "python") -and $ok

if (Get-Command docker -ErrorAction SilentlyContinue) {
    $ok = (Check-NativeCommand "Docker Engine reachable" { docker version 2>$null | Out-Null }) -and $ok
    $ok = (Check-NativeCommand "Docker Compose available" { docker compose version 2>$null | Out-Null }) -and $ok
}

if ($ok) {
    Write-Host "`nENVIRONMENT CHECK: PASS"
    exit 0
}

Write-Host "`nENVIRONMENT CHECK: FAIL"
exit 1
