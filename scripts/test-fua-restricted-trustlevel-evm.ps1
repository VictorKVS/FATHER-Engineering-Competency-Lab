$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

Write-Host "=== FUA-001 WINDOWS RESTRICTED TRUSTLEVEL EVM ==="

$RunAs = Join-Path $env:SystemRoot "System32\runas.exe"
if (-not (Test-Path $RunAs)) {
    Write-Host "RUNAS           : NOT_FOUND"
    Write-Host "RESTRICTED TRUSTLEVEL RESULT: BLOCKED - RUNAS_NOT_AVAILABLE"
    exit 30
}

Write-Host ""
Write-Host "01. Available trust levels"
$levels = & $RunAs /showtrustlevels 2>&1
$levels | ForEach-Object { Write-Host $_ }

$basic = $levels | Where-Object { $_ -match "0x20000" } | Select-Object -First 1
if (-not $basic) {
    Write-Host ""
    Write-Host "RESTRICTED TRUSTLEVEL RESULT: BLOCKED - BASIC_USER_TRUSTLEVEL_NOT_AVAILABLE"
    exit 31
}

Write-Host ""
Write-Host "BASIC USER      : AVAILABLE"

$Root = Join-Path $env:TEMP ("FUA-001-TRUSTLEVEL-EVM-" + [guid]::NewGuid().ToString("N"))
$Out = Join-Path $Root "whoami.txt"
$Cmd = Join-Path $Root "probe.cmd"

try {
    New-Item -ItemType Directory -Force -Path $Root | Out-Null

    @"
@echo off
whoami /all > "$Out"
exit /b %errorlevel%
"@ | Set-Content -Path $Cmd -Encoding ASCII

    Write-Host ""
    Write-Host "02. Launch Basic User trustlevel process"

    $quotedCmd = '"' + $Cmd + '"'
    & $RunAs /trustlevel:0x20000 $quotedCmd
    $launchCode = $LASTEXITCODE
    Write-Host "RUNAS EXIT      : $launchCode"

    $deadline = (Get-Date).AddSeconds(10)
    while (-not (Test-Path $Out) -and (Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 200
    }

    if (-not (Test-Path $Out)) {
        throw "restricted trustlevel child did not produce evidence"
    }

    Write-Host ""
    Write-Host "03. Child token evidence"
    $who = Get-Content $Out
    $who | Select-Object -First 80 | ForEach-Object { Write-Host $_ }

    $denyOnly = $who | Where-Object { $_ -match "Deny only|Только для запрета" } | Select-Object -First 1
    $integrity = $who | Where-Object { $_ -match "Mandatory Label|обязательн" } | Select-Object -First 3

    if ($denyOnly) {
        Write-Host "DENY-ONLY GROUP : PRESENT"
    } else {
        Write-Host "DENY-ONLY GROUP : NOT_OBSERVED"
    }

    if ($integrity) {
        Write-Host "INTEGRITY INFO  : PRESENT"
    } else {
        Write-Host "INTEGRITY INFO  : NOT_OBSERVED"
    }

    Write-Host ""
    Write-Host "WINDOWS RESTRICTED TRUSTLEVEL EVM RESULT: PASS"
}
finally {
    Remove-Item $Root -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path $Root) {
        Write-Host "CLEANUP         : FAIL"
    } else {
        Write-Host "CLEANUP         : PASS"
    }
}
