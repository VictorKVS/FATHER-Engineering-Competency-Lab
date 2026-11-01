param(
    [string]$Distro = "Ubuntu-22.04",
    [string]$Profile = "otus-k8s"
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Kubectl = "/home/vik/.local/bin/kubectl"
$Minikube = "/home/vik/.local/bin/minikube"

function To-WslPath([string]$Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    if ($full -match '^([A-Za-z]):\\(.*)$') {
        return "/mnt/$($Matches[1].ToLowerInvariant())/$($Matches[2] -replace '\\','/')"
    }
    throw "unsupported path: $full"
}

$WslRepo = To-WslPath $Repo
$K8sDir = "$WslRepo/factory/kubernetes/fua-001"

Write-Host "=== FUA-001 STAGE 2.03 / DEPLOYMENT + SERVICE ==="

Write-Host ""
Write-Host "01. Cluster"
& wsl.exe -d $Distro -- $Minikube status -p $Profile
if ($LASTEXITCODE -ne 0) {
    & wsl.exe -d $Distro -- $Minikube start -p $Profile
    if ($LASTEXITCODE -ne 0) { throw "minikube start failed" }
}
& wsl.exe -d $Distro -- $Minikube update-context -p $Profile
if ($LASTEXITCODE -ne 0) { throw "context update failed" }
Write-Host "CLUSTER             : PASS"

Write-Host ""
Write-Host "02. Apply manifests"
& wsl.exe -d $Distro -- $Kubectl apply -f "$K8sDir/namespace.yaml"
if ($LASTEXITCODE -ne 0) { throw "namespace apply failed" }
& wsl.exe -d $Distro -- $Kubectl apply -f "$K8sDir/deployment.yaml"
if ($LASTEXITCODE -ne 0) { throw "deployment apply failed" }
& wsl.exe -d $Distro -- $Kubectl apply -f "$K8sDir/service.yaml"
if ($LASTEXITCODE -ne 0) { throw "service apply failed" }
Write-Host "MANIFEST APPLY      : PASS"

Write-Host ""
Write-Host "03. Rollout"
& wsl.exe -d $Distro -- $Kubectl rollout status deployment/fua-001 -n father-system --timeout=180s
if ($LASTEXITCODE -ne 0) {
    & wsl.exe -d $Distro -- $Kubectl get pods -n father-system -o wide
    & wsl.exe -d $Distro -- $Kubectl describe deployment/fua-001 -n father-system
    throw "deployment rollout failed"
}
& wsl.exe -d $Distro -- $Kubectl get pods -n father-system -o wide
Write-Host "DEPLOYMENT          : PASS"

Write-Host ""
Write-Host "04. Service and endpoints"
$clusterIp = (& wsl.exe -d $Distro -- $Kubectl get service fua-001 -n father-system -o jsonpath='{.spec.clusterIP}').Trim()
$endpoints = (& wsl.exe -d $Distro -- $Kubectl get endpoints fua-001 -n father-system -o jsonpath='{.subsets[*].addresses[*].ip}').Trim()
if (-not $clusterIp) { throw "service ClusterIP missing" }
if (-not $endpoints) { throw "service endpoints missing" }
Write-Host ("CLUSTER IP          : {0}" -f $clusterIp)
Write-Host ("ENDPOINTS           : {0}" -f $endpoints)
Write-Host "SERVICE             : PASS"

Write-Host ""
Write-Host "05. Service path health"
$py = "import urllib.request; print(urllib.request.urlopen('http://fua-001.father-system.svc.cluster.local:8080/health',timeout=5).read().decode())"
$health = & wsl.exe -d $Distro -- $Kubectl exec -n father-system deployment/fua-001 -- python -c $py
if ($LASTEXITCODE -ne 0) { throw "service-path health request failed" }
if (-not ($health -match '"status":"ok"')) { throw "unexpected service health payload: $health" }
Write-Host ("SERVICE HEALTH      : {0}" -f $health)
Write-Host "SERVICE PATH        : PASS"

Write-Host ""
Write-Host "FUA-001 STAGE 2.03 DEPLOYMENT SERVICE RESULT: PASS"
