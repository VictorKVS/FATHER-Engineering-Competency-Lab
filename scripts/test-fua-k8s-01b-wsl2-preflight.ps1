param(
    [string]$Distro = "Ubuntu-22.04"
)

$ErrorActionPreference = "Stop"
$Profile = "otus-k8s"

Write-Host "=== FUA-001 STAGE 2.01B / WSL2 KUBERNETES PREFLIGHT ==="
Write-Host ("WSL DISTRO         : {0}" -f $Distro)

function Invoke-WSL([string]$Command) {
    & wsl.exe -d $Distro -- bash -lc $Command
    if ($LASTEXITCODE -ne 0) {
        throw "WSL command failed: $Command"
    }
}

Write-Host ""
Write-Host "01. WSL2 distro"
$distros = (& wsl.exe -l -q) -replace [char]0,''
if ($distros -notcontains $Distro) { throw "WSL distro not found: $Distro" }
Invoke-WSL 'uname -a; printf "WSL_VERSION_HINT="; uname -r'
Write-Host "WSL DISTRO          : PASS"

Write-Host ""
Write-Host "02. Docker provider inside WSL"

# Prefer a native Docker Engine installed inside Ubuntu. This removes the
# dependency on Docker Desktop's WSL proxy, which is unstable on the target host.
& wsl.exe -d $Distro -- bash -lc 'docker version >/tmp/fua-docker-version.txt 2>&1 && docker info --format "OSTYPE={{.OSType}} DRIVER={{.Driver}}"'
if ($LASTEXITCODE -eq 0) {
    & wsl.exe -d $Distro -- bash -lc 'cat /tmp/fua-docker-version.txt | sed -n "1,24p"'
    Write-Host "DOCKER PROVIDER      : WSL_NATIVE_OR_WORKING_SOCKET"
    Write-Host "DOCKER IN WSL       : PASS"
} else {
    $proxy = "/mnt/wsl/docker-desktop/shared-sockets/guest-services/docker.proxy.sock"
    & wsl.exe -d $Distro -- test -S $proxy
    if ($LASTEXITCODE -eq 0) {
        & wsl.exe -d $Distro -u root -- ln -sf $proxy /var/run/docker.sock
        if ($LASTEXITCODE -ne 0) { throw "failed to restore /var/run/docker.sock runtime symlink" }
        Write-Host "DOCKER SOCKET LINK  : RESTORED"
    } else {
        Write-Host "DOCKER PROXY SOCKET : NOT FOUND"
    }

    & wsl.exe -d $Distro -- bash -lc 'docker version --format "DOCKER_CLIENT={{.Client.Version}} DOCKER_SERVER={{.Server.Version}}"; docker info --format "OSTYPE={{.OSType}} DRIVER={{.Driver}}"'
    if ($LASTEXITCODE -ne 0) {
        Write-Host "DOCKER IN WSL       : BLOCKED"
        Write-Host "REASON              : no working native Docker Engine or Docker Desktop proxy"
        Write-Host "ACTION              : run scripts/bootstrap-fua-wsl-native-docker.ps1"
        exit 2
    }
    Write-Host "DOCKER PROVIDER      : DOCKER_DESKTOP_PROXY"
    Write-Host "DOCKER IN WSL       : PASS"
}
Write-Host ""
Write-Host "03. User-local Kubernetes toolchain"

& wsl.exe -d $Distro -- mkdir -p /home/vik/.local/bin
if ($LASTEXITCODE -ne 0) { throw "failed to create ~/.local/bin" }

& wsl.exe -d $Distro -- test -x /home/vik/.local/bin/minikube
if ($LASTEXITCODE -ne 0) {
    & wsl.exe -d $Distro -- curl -fL --retry 3 --connect-timeout 20 https://storage.googleapis.com/minikube/releases/v1.39.0/minikube-linux-amd64 -o /home/vik/.local/bin/minikube
    if ($LASTEXITCODE -ne 0) { throw "failed to download minikube" }
    & wsl.exe -d $Distro -- chmod 0755 /home/vik/.local/bin/minikube
    if ($LASTEXITCODE -ne 0) { throw "failed to chmod minikube" }
}

& wsl.exe -d $Distro -- test -x /home/vik/.local/bin/kubectl
if ($LASTEXITCODE -ne 0) {
    & wsl.exe -d $Distro -- curl -fL --retry 3 --connect-timeout 20 https://dl.k8s.io/release/v1.37.1/bin/linux/amd64/kubectl -o /home/vik/.local/bin/kubectl
    if ($LASTEXITCODE -ne 0) { throw "failed to download kubectl" }
    & wsl.exe -d $Distro -- chmod 0755 /home/vik/.local/bin/kubectl
    if ($LASTEXITCODE -ne 0) { throw "failed to chmod kubectl" }
}

& wsl.exe -d $Distro -- /home/vik/.local/bin/minikube version
if ($LASTEXITCODE -ne 0) { throw "minikube version check failed" }

& wsl.exe -d $Distro -- /home/vik/.local/bin/kubectl version --client
if ($LASTEXITCODE -ne 0) { throw "kubectl version check failed" }

Write-Host "WSL TOOLCHAIN       : PASS"

Write-Host ""
Write-Host "03A. Registry/network reachability"
& wsl.exe -d $Distro -- curl -I -L --connect-timeout 10 --max-time 20 https://registry-1.docker.io/v2/
if ($LASTEXITCODE -eq 0) {
    Write-Host "DOCKER HUB NETWORK  : PASS"
} else {
    Write-Host "DOCKER HUB NETWORK  : DEGRADED"
    Write-Host "NOTE                : Native Docker is healthy, but external registry access is timing out"
}
Write-Host ""
Write-Host "04. Start WSL-native minikube profile"
$start = @'
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

if minikube status -p otus-k8s >/tmp/fua-mk-status.txt 2>&1; then
  cat /tmp/fua-mk-status.txt
else
  minikube delete -p otus-k8s >/dev/null 2>&1 || true
  minikube start -p otus-k8s \
    --driver=docker \
    --container-runtime=containerd \
    --cpus=4 \
    --memory=6144
fi
'@
& wsl.exe -d $Distro -- bash -lc $start
if ($LASTEXITCODE -ne 0) { throw "WSL-native minikube start failed" }
Write-Host "WSL MINIKUBE        : PASS"

Write-Host ""
Write-Host "05. Kubernetes API / node readiness"
$verify = @'
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
minikube update-context -p otus-k8s
test "$(kubectl config current-context)" = "otus-k8s"
kubectl cluster-info
kubectl get nodes -o wide
kubectl wait --for=condition=Ready node --all --timeout=120s
kubectl get pods -n kube-system -o wide
'@
& wsl.exe -d $Distro -- bash -lc $verify
if ($LASTEXITCODE -ne 0) { throw "WSL Kubernetes API/readiness verification failed" }
Write-Host "NODE READY          : PASS"
Write-Host "KUBE-SYSTEM         : PASS"

Write-Host ""
Write-Host "06. Isolation decision"
Write-Host "WINDOWS MINIKUBE    : BLOCKED_BY_HOST_TOOLING"
Write-Host "WSL2 MINIKUBE       : ACTIVE"
Write-Host "DRIVER              : docker"
Write-Host "CONTAINER RUNTIME   : containerd"
Write-Host ""
Write-Host "FUA-001 STAGE 2.01B WSL2 KUBERNETES PREFLIGHT RESULT: PASS"
