param(
    [string]$Distro = "Ubuntu-22.04"
)

$ErrorActionPreference = "Stop"

Write-Host "=== FUA-001 STAGE 2.01C / WSL2 NATIVE DOCKER ENGINE BOOTSTRAP ==="
Write-Host ("DISTRO              : {0}" -f $Distro)

function Run-Root([string]$Command) {
    & wsl.exe -d $Distro -u root -- bash -lc $Command
    if ($LASTEXITCODE -ne 0) { throw "WSL root command failed: $Command" }
}

function Run-User([string]$Command) {
    & wsl.exe -d $Distro -- bash -lc $Command
    if ($LASTEXITCODE -ne 0) { throw "WSL user command failed: $Command" }
}

Write-Host ""
Write-Host "01. Verify WSL distro"
$distros = (& wsl.exe -l -q) -replace [char]0,''
if ($distros -notcontains $Distro) { throw "WSL distro not found: $Distro" }
Run-User 'uname -a; id'
Write-Host "WSL DISTRO          : PASS"

Write-Host ""
Write-Host "02. Ensure systemd is enabled"
& wsl.exe -d $Distro -- bash -lc 'test "$(ps -p 1 -o comm=)" = "systemd"'
if ($LASTEXITCODE -ne 0) {
    Write-Host "SYSTEMD             : NOT ACTIVE"
    Write-Host "ACTION              : safely enabling systemd in /etc/wsl.conf"

    $enableSystemd = @'
set -euo pipefail
cp -a /etc/wsl.conf /etc/wsl.conf.fua-backup 2>/dev/null || true
if grep -q '^[boot]' /etc/wsl.conf 2>/dev/null; then
  if grep -q '^systemd=' /etc/wsl.conf; then
    sed -i 's/^systemd=.*/systemd=true/' /etc/wsl.conf
  else
    sed -i '/^[boot]/a systemd=true' /etc/wsl.conf
  fi
else
  printf '
[boot]
systemd=true
' >> /etc/wsl.conf
fi
cat /etc/wsl.conf
'@
    Run-Root $enableSystemd
    & wsl.exe --terminate $Distro
    Start-Sleep -Seconds 3
}

Run-User 'test "$(ps -p 1 -o comm=)" = "systemd"; systemctl is-system-running --wait || true'
Write-Host "SYSTEMD             : PASS"

Write-Host ""
Write-Host "03. Remove stale Docker Desktop CLI shim only"
Run-Root 'if [ -L /usr/bin/docker ] && readlink /usr/bin/docker | grep -q "/mnt/wsl/docker-desktop"; then rm -f /usr/bin/docker; fi'
Write-Host "DESKTOP CLI SHIM    : CLEARED"

Write-Host ""
Write-Host "04. Install native Docker Engine from Docker APT repository"
$installDocker = @'
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y ca-certificates curl

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

. /etc/os-release
ARCH="$(dpkg --print-architecture)"
echo "deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl restart docker
'@
Run-Root $installDocker
Write-Host "DOCKER INSTALL      : PASS"

Write-Host ""
Write-Host "05. Grant current WSL user Docker access"
$userName = (& wsl.exe -d $Distro -- bash -lc 'id -un').Trim()
Run-Root "usermod -aG docker $userName"
& wsl.exe --terminate $Distro
Start-Sleep -Seconds 3
Write-Host ("DOCKER GROUP USER   : {0}" -f $userName)

Write-Host ""
Write-Host "06. Verify native engine"
Run-User 'docker version'
Run-User 'docker info --format "OSTYPE={{.OSType}} DRIVER={{.Driver}} ROOT={{.DockerRootDir}}"'
Run-User 'docker run --rm hello-world >/dev/null'
Write-Host "NATIVE DOCKER       : PASS"

Write-Host ""
Write-Host "07. Isolation decision"
Write-Host "DOCKER DESKTOP WSL  : NOT REQUIRED FOR KUBERNETES"
Write-Host "WSL NATIVE ENGINE   : ACTIVE"
Write-Host "MINIKUBE DRIVER     : docker"
Write-Host ""
Write-Host "FUA-001 STAGE 2.01C WSL2 NATIVE DOCKER RESULT: PASS"
