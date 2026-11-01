param(
    [string]$Distro = "Ubuntu-22.04"
)

$ErrorActionPreference = "Stop"

Write-Host "=== FUA-001 STAGE 2.01C / WSL2 NATIVE DOCKER ENGINE BOOTSTRAP ==="
Write-Host ("DISTRO              : {0}" -f $Distro)

function WslRoot {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    & wsl.exe -d $Distro -u root -- @Args
    if ($LASTEXITCODE -ne 0) { throw "WSL root command failed: $($Args -join ' ')" }
}

function WslUser {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    & wsl.exe -d $Distro -- @Args
    if ($LASTEXITCODE -ne 0) { throw "WSL user command failed: $($Args -join ' ')" }
}

Write-Host ""
Write-Host "01. Verify WSL distro"
$distros = (& wsl.exe -l -q) -replace [char]0,''
if ($distros -notcontains $Distro) { throw "WSL distro not found: $Distro" }
WslUser uname -a
WslUser id
Write-Host "WSL DISTRO          : PASS"

Write-Host ""
Write-Host "02. Ensure systemd is enabled"
$pid1 = (& wsl.exe -d $Distro -- ps -p 1 -o comm=).Trim()
if ($pid1 -ne "systemd") {
    Write-Host ("PID1                : {0}" -f $pid1)
    Write-Host "SYSTEMD             : NOT ACTIVE"
    Write-Host "ACTION              : enable systemd in /etc/wsl.conf"

    WslRoot cp -a /etc/wsl.conf /etc/wsl.conf.fua-backup
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
    WslRoot rm -f /usr/bin/docker
    Write-Host "DESKTOP CLI SHIM    : REMOVED"
} else {
    Write-Host "DESKTOP CLI SHIM    : NOT PRESENT"
}

Write-Host ""
Write-Host "04. Install native Docker Engine"
WslRoot env DEBIAN_FRONTEND=noninteractive apt-get update
WslRoot env DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl
WslRoot install -m 0755 -d /etc/apt/keyrings
WslRoot curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
WslRoot chmod a+r /etc/apt/keyrings/docker.asc

$codename = (& wsl.exe -d $Distro -- sh -c ". /etc/os-release; printf %s \$VERSION_CODENAME").Trim()
$arch = (& wsl.exe -d $Distro -- dpkg --print-architecture).Trim()
if (-not $codename -or -not $arch) { throw "failed to resolve Ubuntu codename/architecture" }

$repoLine = "deb [arch=$arch signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $codename stable"
& wsl.exe -d $Distro -u root -- sh -c "printf '%s\n' '$repoLine' > /etc/apt/sources.list.d/docker.list"
if ($LASTEXITCODE -ne 0) { throw "failed to configure Docker apt repository" }

WslRoot env DEBIAN_FRONTEND=noninteractive apt-get update
WslRoot env DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
WslRoot systemctl enable docker
WslRoot systemctl restart docker
Write-Host "DOCKER INSTALL      : PASS"

Write-Host ""
Write-Host "05. Grant user Docker access"
$userName = (& wsl.exe -d $Distro -- id -un).Trim()
WslRoot usermod -aG docker $userName
& wsl.exe --terminate $Distro
Start-Sleep -Seconds 3
Write-Host ("DOCKER GROUP USER   : {0}" -f $userName)

Write-Host ""
Write-Host "06. Verify native engine"
WslUser docker version
WslUser docker info
WslUser docker run --rm hello-world
Write-Host "NATIVE DOCKER       : PASS"

Write-Host ""
Write-Host "07. Isolation decision"
Write-Host "DOCKER DESKTOP WSL  : NOT REQUIRED FOR KUBERNETES"
Write-Host "WSL NATIVE ENGINE   : ACTIVE"
Write-Host "MINIKUBE DRIVER     : docker"
Write-Host ""
Write-Host "FUA-001 STAGE 2.01C WSL2 NATIVE DOCKER RESULT: PASS"
