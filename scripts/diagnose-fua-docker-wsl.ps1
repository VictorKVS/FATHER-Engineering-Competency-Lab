$ErrorActionPreference = "Continue"

Write-Host "=== FUA-001 DOCKER / WSL DIAGNOSTIC ==="

$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
Write-Host ("DOCKER CLI       : {0}" -f ($(if($dockerCmd){$dockerCmd.Source}else{"NOT_FOUND"})))

Write-Host ""
Write-Host "01. Docker Desktop installation discovery"

$candidates = New-Object System.Collections.Generic.List[string]

$fixed = @(
    "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
    "$Env:ProgramFiles\Docker\Docker\DockerCli.exe",
    "$Env:LocalAppData\Docker\Docker Desktop.exe"
)
foreach($p in $fixed){
    if($p -and (Test-Path $p)){ $candidates.Add($p) }
}

$regRoots = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
)
foreach($root in $regRoots){
    Get-ItemProperty $root -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -like "Docker Desktop*" } |
        ForEach-Object {
            Write-Host ("INSTALLED APP     : {0} {1}" -f $_.DisplayName,$_.DisplayVersion)
            if($_.InstallLocation){
                $p=Join-Path $_.InstallLocation "Docker Desktop.exe"
                if(Test-Path $p){ $candidates.Add($p) }
            }
        }
}

$candidates = $candidates | Select-Object -Unique
if($candidates.Count -eq 0){
    Write-Host "DOCKER DESKTOP   : NOT_FOUND"
}else{
    $candidates | ForEach-Object { Write-Host ("DOCKER DESKTOP   : {0}" -f $_) }
}

Write-Host ""
Write-Host "02. Docker services/processes"
Get-Service -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "*docker*" -or $_.DisplayName -like "*Docker*" } |
    ForEach-Object { Write-Host ("SERVICE          : {0} [{1}]" -f $_.Name,$_.Status) }

Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -like "*docker*" -or $_.ProcessName -like "*com.docker*" } |
    ForEach-Object { Write-Host ("PROCESS          : {0} PID={1}" -f $_.ProcessName,$_.Id) }

Write-Host ""
Write-Host "03. WSL status"
$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
if(-not $wsl){
    Write-Host "WSL              : NOT_FOUND"
}else{
    & wsl.exe --status 2>&1 | ForEach-Object { Write-Host ("WSL STATUS       : {0}" -f $_) }
    & wsl.exe -l -v 2>&1 | ForEach-Object { Write-Host ("WSL DISTRO       : {0}" -f $_) }
}

Write-Host ""
Write-Host "04. Docker contexts"
if($dockerCmd){
    & docker context ls 2>&1 | ForEach-Object { Write-Host $_ }
}

Write-Host ""
Write-Host "05. Attempt start existing Docker Desktop"
$desktopExe = $candidates | Where-Object { $_ -like "*Docker Desktop.exe" } | Select-Object -First 1
if($desktopExe){
    Start-Process -FilePath $desktopExe | Out-Null
    Write-Host ("START REQUEST    : {0}" -f $desktopExe)

    $ready=$false
    for($i=1;$i -le 60;$i++){
        Start-Sleep -Seconds 2
        & docker info *> $null
        if($LASTEXITCODE -eq 0){
            $ready=$true
            break
        }
    }
    if($ready){
        Write-Host "DOCKER ENGINE    : READY"
        Write-Host "DOCKER/WSL DIAGNOSTIC RESULT: PASS"
        exit 0
    }
    Write-Host "DOCKER ENGINE    : START_TIMEOUT"
    Write-Host "DOCKER/WSL DIAGNOSTIC RESULT: BLOCKED"
    exit 31
}

if(-not $dockerCmd){
    Write-Host "ROOT CAUSE       : DOCKER_CLI_NOT_INSTALLED"
    Write-Host "DOCKER/WSL DIAGNOSTIC RESULT: BLOCKED"
    exit 32
}

Write-Host "ROOT CAUSE       : DOCKER_DESKTOP_NOT_INSTALLED_OR_NOT_DISCOVERABLE"
Write-Host "DOCKER/WSL DIAGNOSTIC RESULT: BLOCKED"
exit 33
