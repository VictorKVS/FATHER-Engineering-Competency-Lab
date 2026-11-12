$ErrorActionPreference = "Stop"

$service = "father-chassis"
$image = "father-chassis-father-chassis:latest"
$artifactDir = Join-Path $PSScriptRoot "..\artifacts\security"
$artifactDir = [System.IO.Path]::GetFullPath($artifactDir)
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null

function Require-Docker {
    docker version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Docker is required for G6.3" }
}

function Read-JsonFile([string]$path) {
    if (-not (Test-Path $path)) { throw "Expected report missing: $path" }
    return Get-Content $path -Raw | ConvertFrom-Json
}

function Ensure-ScannerImage([string]$imageName, [int]$attempts = 4) {
    # Windows PowerShell 5.1 can convert stderr from native commands into
    # NativeCommandError when ErrorActionPreference=Stop. Image absence is an
    # expected branch here, so inspect/pull must be handled by exit code.
    $savedPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        & docker image inspect $imageName *> $null
        $inspectExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $savedPreference
    }

    if ($inspectExit -eq 0) {
        Write-Host "Scanner image already available locally: $imageName"
        return
    }

    for ($attempt = 1; $attempt -le $attempts; $attempt++) {
        Write-Host "Pull scanner image $imageName (attempt $attempt/$attempts)"

        $savedPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = "Continue"
            & docker pull $imageName
            $pullExit = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $savedPreference
        }

        if ($pullExit -eq 0) {
            Write-Host "Scanner image ready: $imageName"
            return
        }

        Write-Warning "Pull attempt $attempt failed for $imageName (exit code $pullExit)"
        if ($attempt -lt $attempts) {
            Start-Sleep -Seconds ([Math]::Min(5 * $attempt, 15))
        }
    }

    throw "INFRASTRUCTURE_ERROR: could not obtain scanner image '$imageName' from registry after $attempts attempts. Security qualification was NOT executed and must not be marked FAIL."
}

Write-Host "[G6.3 1/8] Validate Docker and canonical image"
Require-Docker
docker image inspect $image | Out-Null
if ($LASTEXITCODE -ne 0) {
    docker compose build $service
    if ($LASTEXITCODE -ne 0) { throw "Could not build canonical image" }
}

Write-Host "[G6.3 2/8] Check running-container hardening"
$containerId = (docker compose ps -q $service).Trim()
if ([string]::IsNullOrWhiteSpace($containerId)) { throw "canonical father-chassis container is not running" }
$inspect = docker inspect $containerId | ConvertFrom-Json
$c = $inspect[0]

$containerUser = [string]$c.Config.User
$securityOpt = @($c.HostConfig.SecurityOpt)
$memoryLimit = [int64]$c.HostConfig.Memory
$nanoCpus = [int64]$c.HostConfig.NanoCpus

$nonRoot = (
    -not [string]::IsNullOrWhiteSpace($containerUser) -and
    $containerUser -notin @("0", "root")
)
$noNewPrivileges = @($securityOpt | Where-Object { $_ -match "no-new-privileges" }).Count -gt 0
$memoryLimited = $memoryLimit -gt 0
$cpuLimited = $nanoCpus -gt 0

if (-not $nonRoot) { throw "container is not running as non-root user: '$containerUser'" }
if (-not $noNewPrivileges) { throw "no-new-privileges is not enabled" }
if (-not $memoryLimited) { throw "container memory limit is missing" }
if (-not $cpuLimited) { throw "container CPU limit is missing" }

Write-Host "[G6.3 3/8] Prepare scanner images and generate CycloneDX SBOM with Trivy"
Ensure-ScannerImage "aquasec/trivy:latest"
Ensure-ScannerImage "zricethezav/gitleaks:latest"
Ensure-ScannerImage "semgrep/semgrep:latest"

$sbomPath = Join-Path $artifactDir "father-chassis-sbom.cdx.json"
docker run --rm --pull=never -v /var/run/docker.sock:/var/run/docker.sock -v "$($artifactDir):/out" aquasec/trivy:latest image --quiet --format cyclonedx --output /out/father-chassis-sbom.cdx.json $image
if ($LASTEXITCODE -ne 0) { throw "Trivy CycloneDX SBOM generation failed" }
$sbom = Read-JsonFile $sbomPath
if ([string]::IsNullOrWhiteSpace([string]$sbom.bomFormat)) { throw "invalid CycloneDX SBOM" }

Write-Host "[G6.3 4/8] Scan canonical image vulnerabilities with Trivy"
$trivyPath = Join-Path $artifactDir "trivy-vulnerabilities.json"
docker run --rm --pull=never -v /var/run/docker.sock:/var/run/docker.sock -v "$($artifactDir):/out" aquasec/trivy:latest image --quiet --format json --output /out/trivy-vulnerabilities.json --severity HIGH,CRITICAL $image
if ($LASTEXITCODE -ne 0) { throw "Trivy vulnerability scan execution failed" }
$trivy = Read-JsonFile $trivyPath
$vulns = @()
foreach ($result in @($trivy.Results)) {
    $vulns += @($result.Vulnerabilities)
}
$criticalVulns = @($vulns | Where-Object { $_.Severity -eq "CRITICAL" })
$highVulns = @($vulns | Where-Object { $_.Severity -eq "HIGH" })
if ($criticalVulns.Count -gt 0) {
    throw "Trivy found $($criticalVulns.Count) CRITICAL vulnerabilities"
}

Write-Host "[G6.3 5/8] Scan repository for secrets with Gitleaks"
$repoPath = (Get-Location).Path
$gitleaksPath = Join-Path $artifactDir "gitleaks.json"
docker run --rm --pull=never -v "$($repoPath):/repo" zricethezav/gitleaks:latest detect --source=/repo --no-git --report-format=json --report-path=/repo/artifacts/security/gitleaks.json --exit-code=0
if ($LASTEXITCODE -ne 0) { throw "Gitleaks execution failed" }
if (-not (Test-Path $gitleaksPath)) { "[]" | Set-Content -Encoding UTF8 $gitleaksPath }
$gitleaks = @(Get-Content $gitleaksPath -Raw | ConvertFrom-Json)
if ($gitleaks.Count -gt 0) {
    throw "Gitleaks found $($gitleaks.Count) potential secrets"
}

Write-Host "[G6.3 6/8] Run Bandit Python SAST"
$banditPath = Join-Path $artifactDir "bandit.json"
docker run --rm -v "$($repoPath):/repo" python:3.12-slim sh -c "pip install --quiet bandit && bandit -r /repo/src/father -f json -o /repo/artifacts/security/bandit.json || true"
if ($LASTEXITCODE -ne 0) { throw "Bandit execution failed" }
$bandit = Read-JsonFile $banditPath
$banditHigh = @($bandit.results | Where-Object { $_.issue_severity -eq "HIGH" })
if ($banditHigh.Count -gt 0) {
    throw "Bandit found $($banditHigh.Count) HIGH severity findings"
}

Write-Host "[G6.3 7/8] Run Semgrep SAST"
$semgrepPath = Join-Path $artifactDir "semgrep.json"
docker run --rm --pull=never -v "$($repoPath):/src" semgrep/semgrep:latest semgrep scan --config auto --json --output /src/artifacts/security/semgrep.json /src/src/father
if ($LASTEXITCODE -ne 0) { throw "Semgrep execution failed" }
$semgrep = Read-JsonFile $semgrepPath
$semgrepBlocking = @(
    $semgrep.results | Where-Object {
        $severity = [string]$_.extra.severity
        $severity -in @("ERROR", "CRITICAL", "HIGH")
    }
)
if ($semgrepBlocking.Count -gt 0) {
    throw "Semgrep found $($semgrepBlocking.Count) blocking findings"
}

Write-Host "[G6.3 8/8] Produce qualification summary"
$result = [ordered]@{
    qualification = "G6.3_SECURITY_SUPPLY_CHAIN"
    passed = $true
    canonical_image = $image
    hardening = [ordered]@{
        container_user = $containerUser
        non_root = $nonRoot
        no_new_privileges = $noNewPrivileges
        memory_limit_bytes = $memoryLimit
        nano_cpus = $nanoCpus
    }
    sbom = [ordered]@{
        format = [string]$sbom.bomFormat
        spec_version = [string]$sbom.specVersion
        path = "artifacts/security/father-chassis-sbom.cdx.json"
    }
    trivy = [ordered]@{
        critical = $criticalVulns.Count
        high = $highVulns.Count
        report = "artifacts/security/trivy-vulnerabilities.json"
    }
    gitleaks = [ordered]@{
        findings = $gitleaks.Count
        report = "artifacts/security/gitleaks.json"
    }
    bandit = [ordered]@{
        high = $banditHigh.Count
        total = @($bandit.results).Count
        report = "artifacts/security/bandit.json"
    }
    semgrep = [ordered]@{
        blocking = $semgrepBlocking.Count
        total = @($semgrep.results).Count
        report = "artifacts/security/semgrep.json"
    }
}

$summaryPath = Join-Path $artifactDir "g6_3_security_supply_chain_summary.json"
$result | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 $summaryPath

Write-Host ""
Write-Host "G6.3 SECURITY + SUPPLY CHAIN QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 12
