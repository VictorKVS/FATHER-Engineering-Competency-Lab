$ErrorActionPreference = "Stop"

Write-Host "=== FUA-001 STAGE 2.01 / KUBERNETES PREFLIGHT ==="

$Profile = "otus-k8s"
$ExpectedDriver = "docker"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

function Resolve-CommandPath([string]$Name, [string[]]$Fallbacks=@()) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($p in $Fallbacks) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$Docker = Resolve-CommandPath "docker" @(
    "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe",
    "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe"
)
$Minikube = Resolve-CommandPath "minikube" @(
    "$env:ProgramFiles\Kubernetes\Minikube\minikube.exe",
    "$env:USERPROFILE\minikube.exe"
)
$Kubectl = Resolve-CommandPath "kubectl" @(
    "$env:ProgramFiles\Docker\Docker\resources\bin\kubectl.exe",
    "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\kubectl.exe"
)

if (-not $Docker) { throw "Docker CLI not found" }
if (-not $Minikube) { throw "minikube not found" }
if (-not $Kubectl) { throw "kubectl not found" }

Write-Host ""
Write-Host "01. Toolchain"
Write-Host ("DOCKER   : {0}" -f $Docker)
Write-Host ("MINIKUBE : {0}" -f $Minikube)
Write-Host ("KUBECTL  : {0}" -f $Kubectl)

& $Docker version --format "DOCKER_CLIENT={{.Client.Version}} DOCKER_SERVER={{.Server.Version}}"
if ($LASTEXITCODE -ne 0) { throw "Docker Engine unavailable" }

& $Minikube version
if ($LASTEXITCODE -ne 0) { throw "minikube version failed" }

& $Kubectl version --client
if ($LASTEXITCODE -ne 0) { throw "kubectl client version failed" }
Write-Host "TOOLCHAIN           : PASS"

Write-Host ""
Write-Host "02. WSL / Docker context diagnostics"
try { wsl.exe --status } catch { Write-Host ("WSL STATUS WARNING : {0}" -f $_.Exception.Message) }
& $Docker context show
if ($LASTEXITCODE -ne 0) { throw "docker context query failed" }
Write-Host "HOST RUNTIME        : PASS"

Write-Host ""
Write-Host "03. Minikube profile"
$ProfileExists = $false
$ProfileJson = $null
try {
    $Raw = & $Minikube profile list -o json 2>$null
    if ($LASTEXITCODE -eq 0 -and $Raw) {
        $ProfileJson = $Raw | ConvertFrom-Json
        $profiles = @()
        if ($ProfileJson.valid) { $profiles += @($ProfileJson.valid) }
        if ($ProfileJson.invalid) { $profiles += @($ProfileJson.invalid) }
        $ProfileExists = @($profiles | Where-Object { $_.Name -eq $Profile }).Count -gt 0
    }
} catch {
    Write-Host ("PROFILE LIST WARNING : {0}" -f $_.Exception.Message)
}

if (-not $ProfileExists) {
    Write-Host "PROFILE             : NOT FOUND"
    Write-Host "ACTION              : CREATE NON-DESTRUCTIVE PROFILE"
    & $Minikube start -p $Profile --driver=$ExpectedDriver --cpus=4 --memory=6144 --apiserver-name=control-plane.minikube.internal --apiserver-names=localhost,control-plane.minikube.internal
    if ($LASTEXITCODE -ne 0) { throw "minikube profile creation/start failed" }
} else {
    Write-Host "PROFILE             : FOUND"
    $status = & $Minikube status -p $Profile --output json 2>$null
    $running = $false
    if ($LASTEXITCODE -eq 0 -and $status) {
        try {
            $sj = $status | ConvertFrom-Json
            $running = ($sj.Host -eq "Running" -and $sj.Kubelet -eq "Running" -and $sj.APIServer -eq "Running")
            Write-Host ("HOST                : {0}" -f $sj.Host)
            Write-Host ("KUBELET             : {0}" -f $sj.Kubelet)
            Write-Host ("APISERVER           : {0}" -f $sj.APIServer)
        } catch {}
    }
    if (-not $running) {
        Write-Host "ACTION              : START EXISTING PROFILE"
        & $Minikube start -p $Profile --apiserver-name=control-plane.minikube.internal --apiserver-names=localhost,control-plane.minikube.internal
        if ($LASTEXITCODE -ne 0) { throw "minikube start existing profile failed" }
    }
}
Write-Host "MINIKUBE PROFILE    : PASS"

Write-Host ""
Write-Host "04. Bind kubectl context"
& $Minikube update-context -p $Profile
if ($LASTEXITCODE -ne 0) { throw "minikube update-context failed" }

$Context = (& $Kubectl config current-context).Trim()
Write-Host ("CURRENT CONTEXT     : {0}" -f $Context)
if ($Context -notmatch [regex]::Escape($Profile)) {
    throw "kubectl current context is not bound to $Profile"
}
Write-Host "KUBECTL CONTEXT     : PASS"

Write-Host ""
Write-Host "05. Kubernetes API / node readiness"
& $Kubectl cluster-info
if ($LASTEXITCODE -ne 0) { throw "Kubernetes API unavailable" }

& $Kubectl get nodes -o wide
if ($LASTEXITCODE -ne 0) { throw "kubectl get nodes failed" }

$NotReady = & $Kubectl get nodes --no-headers 2>$null | Where-Object { $_ -notmatch "\sReady\s" }
if ($NotReady) {
    Write-Host $NotReady
    throw "one or more Kubernetes nodes are not Ready"
}
Write-Host "NODE READY          : PASS"

Write-Host ""
Write-Host "06. kube-system health"
& $Kubectl get pods -n kube-system -o wide
if ($LASTEXITCODE -ne 0) { throw "cannot query kube-system" }

$BadPods = & $Kubectl get pods -n kube-system --no-headers 2>$null | Where-Object {
    $_ -match "\s(Pending|Failed|Unknown|CrashLoopBackOff|ImagePullBackOff|ErrImagePull)\s"
}
if ($BadPods) {
    Write-Host $BadPods
    throw "kube-system contains unhealthy core workloads"
}
Write-Host "KUBE-SYSTEM         : PASS"

Write-Host ""
Write-Host "07. Cluster summary"
& $Minikube status -p $Profile
& $Kubectl get namespaces
Write-Host ""
Write-Host "FUA-001 STAGE 2.01 KUBERNETES PREFLIGHT RESULT: PASS"
