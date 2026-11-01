param(
    [string]$Distro = "Ubuntu-22.04"
)

$ErrorActionPreference = "Stop"

Write-Host "=== FUA-001 STAGE 2.01C / WSL2 NATIVE DOCKER ENGINE BOOTSTRAP ==="
Write-Host ("DISTRO              : {0}" -f $Distro)

function Invoke-WslRoot {
    param([string[]]$CommandArgs)
    & wsl.exe -d $Distro -u root -- @CommandArgs
    if ($LASTEXITCODE -ne 0) { throw "WSL root command failed: $($CommandArgs -join ' ')" }
}

function Invoke-WslUser {
    param([string[]]$CommandArgs)
    & wsl.exe -d $Distro -- @CommandArgs
    if ($LASTEXITCODE -ne 0) { throw "WSL user command failed: $($CommandArgs -join ' ')" }
}

Write-Host ""
Write-Host "01. Verify WSL distro"
$distros = (& wsl.exe -l -q) -replace [char]0,''
if ($distros -notcontains $Distro) { throw "WSL distro not found: $Distro" }
Invoke-WslUser @("uname","-a")
Invoke-WslUser @("id")
Write-Host "WSL DISTRO          : PASS"

Write-Host ""
Write-Host "02. Ensure systemd is enabled"
$pid1 = (& wsl.exe -d $Distro -- ps -p 1 -o comm=).Trim()
if ($pid1 -ne "systemd") {
    Write-Host ("PID1                : {0}" -f $pid1)
    Write-Host "SYSTEMD             : NOT ACTIVE"
    Write-Host "ACTION              : enable systemd in /etc/wsl.conf"

    Invoke-WslRoot @("cp","-a","/etc/wsl.conf","/etc/wsl.conf.fua-backup")
    & wsl.exe -d $Distro -u root -- sh -c "grep -q '^\[boot\]' /etc/wsl.conf || printf '\n[boot]\n' >> /etc/wsl.conf"
    if ($LASTEXITCODE -ne 0) { throw "failed to ensure [boot] section" }
    & wsl.exe -d $Distro -u root -- sh -c "grep -q '^systemd=' /etc/wsl.conf && sed -i 's/^systemd=.*/systemd=true/' /etc/wsl.conf || sed -i '/^\[boot\]/a systemd=true' /etc/wsl.conf"
    if ($LASTEXITCODE -ne 0) { throw "failed to enable systemd in wsl.conf" }

    & wsl.exe -d $Distro -- cat /etc/wsl.conf
    & wsl.exe --terminate $Distro
    Start-Sleep -Seconds 3
}

$pid1 = (& wsl.exe -d $Distro -- ps -p 1 -o comm=).Trim()
if ($pid1 -ne "systemd") { throw "systemd did not become PID 1" }
Write-Host "SYSTEMD             : PASS"

Write-Host ""
Write-Host "03. Remove only stale Docker Desktop CLI symlink"
$dockerLink = (& wsl.exe -d $Distro -- readlink /usr/bin/docker 2>$null)
if ($dockerLink -like "/mnt/wsl/docker-desktop/*") {
    Invoke-WslRoot @("rm","-f","/usr/bin/docker")
    Write-Host "DESKTOP CLI SHIM    : REMOVED"
} else {
    Write-Host "DESKTOP CLI SHIM    : NOT PRESENT"
}

Write-Host ""
Write-Host "04. Install native Docker Engine"
Invoke-WslRoot @("env","DEBIAN_FRONTEND=noninteractive","apt-get","update")
Invoke-WslRoot @("env","DEBIAN_FRONTEND=noninteractive","apt-get","install","-y","ca-certificates","curl")
Invoke-WslRoot @("install","-m","0755","-d","/etc/apt/keyrings")
Invoke-WslRoot @("curl","-fsSL","https://download.docker.com/linux/ubuntu/gpg","-o","/etc/apt/keyrings/docker.asc")
Invoke-WslRoot @("chmod","a+r","/etc/apt/keyrings/docker.asc")

$osRelease = & wsl.exe -d $Distro -- cat /etc/os-release
if ($LASTEXITCODE -ne 0) { throw "failed to read /etc/os-release" }

$codenameLine = $osRelease | Where-Object { $_ -like "VERSION_CODENAME=*" } | Select-Object -First 1
if (-not $codenameLine) { throw "VERSION_CODENAME not found in /etc/os-release" }
$codename = ($codenameLine -split "=",2)[1].Trim().Trim('"')

$arch = (& wsl.exe -d $Distro -- dpkg --print-architecture).Trim()
if (-not $codename -or -not $arch) { throw "failed to resolve Ubuntu codename/architecture" }

$repoLine = "deb [arch=$arch signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $codename stable"
$repoLine | & wsl.exe -d $Distro -u root -- tee /etc/apt/sources.list.d/docker.list | Out-Null
if ($LASTEXITCODE -ne 0) { throw "failed to configure Docker apt repository" }

Invoke-WslRoot @("env","DEBIAN_FRONTEND=noninteractive","apt-get","update")
Invoke-WslRoot @("env","DEBIAN_FRONTEND=noninteractive","apt-get","install","-y","docker-ce","docker-ce-cli","containerd.io","docker-buildx-plugin","docker-compose-plugin")
Invoke-WslRoot @("systemctl","enable","docker")
Invoke-WslRoot @("systemctl","restart","docker")
Write-Host "DOCKER INSTALL      : PASS"

Write-Host ""
Write-Host "05. Grant user Docker access"
$userName = (& wsl.exe -d $Distro -- id -un).Trim()
Invoke-WslRoot @("usermod","-aG","docker",$userName)
& wsl.exe --terminate $Distro
Start-Sleep -Seconds 3
Write-Host ("DOCKER GROUP USER   : {0}" -f $userName)

Write-Host ""
Write-Host "06. Verify native engine"
Invoke-WslUser @("docker","version")
Invoke-WslUser @("docker","info")
Invoke-WslUser @("docker","run","--rm","hello-world")
Write-Host "NATIVE DOCKER       : PASS"

Write-Host ""
Write-Host "07. Isolation decision"
Write-Host "DOCKER DESKTOP WSL  : NOT REQUIRED FOR KUBERNETES"
Write-Host "WSL NATIVE ENGINE   : ACTIVE"
Write-Host "MINIKUBE DRIVER     : docker"
Write-Host ""
Write-Host "FUA-001 STAGE 2.01C WSL2 NATIVE DOCKER RESULT: PASS"
