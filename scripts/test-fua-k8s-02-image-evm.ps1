param(
    [string]$Distro = "Ubuntu-22.04",
    [string]$Profile = "otus-k8s",
    [string]$Image = "father/fua-001:k8s-0.1"
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function To-WslPath([string]$Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    if ($full -match '^([A-Za-z]):\\(.*)$') {
        $drive = $Matches[1].ToLowerInvariant()
        $tail = $Matches[2] -replace '\\','/'
        return "/mnt/$drive/$tail"
    }
    throw "unsupported Windows path for WSL conversion: $full"
}

$WslRepo = To-WslPath $Repo
$Dockerfile = "$WslRepo/Dockerfile"
$Minikube = "/home/vik/.local/bin/minikube"

Write-Host "=== FUA-001 STAGE 2.02 / KUBERNETES IMAGE ==="

Write-Host ""
Write-Host "01. Prerequisites"
& wsl.exe -d $Distro -- docker version --format "CLIENT={{.Client.Version}} SERVER={{.Server.Version}}"
if ($LASTEXITCODE -ne 0) { throw "native Docker Engine unavailable in WSL" }
& wsl.exe -d $Distro -- $Minikube status -p $Profile
if ($LASTEXITCODE -ne 0) { throw "minikube profile is not running" }
Write-Host "PREREQUISITES       : PASS"

Write-Host ""
Write-Host "02. Build image"
& wsl.exe -d $Distro -- docker build --pull --file $Dockerfile --tag $Image $WslRepo
if ($LASTEXITCODE -ne 0) { throw "FUA image build failed" }
Write-Host "IMAGE BUILD         : PASS"

Write-Host ""
Write-Host "03. Inspect image identity and runtime user"
$imageId = (& wsl.exe -d $Distro -- docker image inspect $Image --format '{{.Id}}').Trim()
$user = (& wsl.exe -d $Distro -- docker image inspect $Image --format '{{.Config.User}}').Trim()
if (-not $imageId) { throw "image id missing" }
if ($user -eq "" -or $user -eq "0" -or $user -match '^0:') { throw "image runtime user is root" }
Write-Host ("IMAGE ID            : {0}" -f $imageId)
Write-Host ("RUNTIME USER        : {0}" -f $user)
Write-Host "NON-ROOT            : PASS"

Write-Host ""
Write-Host "04. Run container and verify health"
$containerName = "fua-001-k8s-image-test"
& wsl.exe -d $Distro -- docker rm -f $containerName 2>$null | Out-Null
& wsl.exe -d $Distro -- docker run -d --name $containerName --read-only --tmpfs /tmp:rw,noexec,nosuid,size=32m --cap-drop ALL --security-opt no-new-privileges --memory 256m -p 127.0.0.1:18080:8080 $Image
if ($LASTEXITCODE -ne 0) { throw "container start failed" }

try {
    $healthy = $false
    for ($i=0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        $health = (& wsl.exe -d $Distro -- docker inspect $containerName --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}').Trim()
        if ($health -eq "healthy") { $healthy = $true; break }
        if ($health -eq "unhealthy") { break }
    }
    if (-not $healthy) {
        & wsl.exe -d $Distro -- docker logs $containerName
        throw "container did not become healthy"
    }

    $json = & wsl.exe -d $Distro -- curl -fsS http://127.0.0.1:18080/health
    if ($LASTEXITCODE -ne 0) { throw "health endpoint request failed" }
    $healthObj = $json | ConvertFrom-Json
    if ($healthObj.status -ne "ok") { throw "unexpected health response" }

    $uid = (& wsl.exe -d $Distro -- docker exec $containerName id -u).Trim()
    if ($uid -eq "0") { throw "running container is root" }

    Write-Host ("HEALTH RESPONSE     : {0}" -f $json)
    Write-Host ("RUNTIME UID         : {0}" -f $uid)
    Write-Host "CONTAINER HEALTH    : PASS"
}
finally {
    & wsl.exe -d $Distro -- docker rm -f $containerName 2>$null | Out-Null
}

Write-Host ""
Write-Host "05. Load image into Minikube"
& wsl.exe -d $Distro -- $Minikube image load -p $Profile $Image
if ($LASTEXITCODE -ne 0) { throw "minikube image load failed" }

& wsl.exe -d $Distro -- $Minikube image ls -p $Profile
if ($LASTEXITCODE -ne 0) { throw "minikube image ls failed" }

$imageList = & wsl.exe -d $Distro -- $Minikube image ls -p $Profile
if (-not ($imageList -match 'father/fua-001')) { throw "FUA image not found in minikube image store" }
Write-Host "MINIKUBE IMAGE      : PASS"

Write-Host ""
Write-Host "06. Result"
Write-Host ("IMAGE               : {0}" -f $Image)
Write-Host ("IMAGE ID            : {0}" -f $imageId)
Write-Host "FUA-001 STAGE 2.02 KUBERNETES IMAGE RESULT: PASS"
