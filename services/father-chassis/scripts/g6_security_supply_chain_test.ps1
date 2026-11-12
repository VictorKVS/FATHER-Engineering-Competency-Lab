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

function Resolve-ScannerImage([string[]]$candidates, [int]$attemptsPerCandidate = 3) {
    foreach ($imageName in $candidates) {
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
            return $imageName
        }
    }

    foreach ($imageName in $candidates) {
        for ($attempt = 1; $attempt -le $attemptsPerCandidate; $attempt++) {
            Write-Host "Pull scanner image $imageName (attempt $attempt/$attemptsPerCandidate)"

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
                return $imageName
            }

            Write-Warning "Pull attempt $attempt failed for $imageName (exit code $pullExit)"
            if ($attempt -lt $attemptsPerCandidate) {
                Start-Sleep -Seconds ([Math]::Min(5 * $attempt, 15))
            }
        }

        Write-Warning "Registry candidate unavailable: $imageName"
    }

    throw "INFRASTRUCTURE_ERROR: could not obtain any scanner image candidate: $($candidates -join ', '). Security qualification was NOT executed and must not be marked FAIL."
}

Write-Host "[G6.3 1/8] Validate Docker and canonical image"
Require-Docker
Write-Host "Build canonical image from current source before security qualification"
docker compose build $service
if ($LASTEXITCODE -ne 0) {
    throw "INFRASTRUCTURE_ERROR: could not build canonical image from current source"
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
$trivyImage = Resolve-ScannerImage @(
    "ghcr.io/aquasecurity/trivy:latest",
    "aquasec/trivy:latest"
)
$gitleaksImage = Resolve-ScannerImage @(
    "zricethezav/gitleaks:latest"
)
$semgrepImage = Resolve-ScannerImage @(
    "semgrep/semgrep:latest"
)

$sbomPath = Join-Path $artifactDir "father-chassis-sbom.cdx.json"
docker run --rm --pull=never -v /var/run/docker.sock:/var/run/docker.sock -v "$($artifactDir):/out" $trivyImage image --quiet --format cyclonedx --output /out/father-chassis-sbom.cdx.json $image
if ($LASTEXITCODE -ne 0) { throw "Trivy CycloneDX SBOM generation failed" }
$sbom = Read-JsonFile $sbomPath
if ([string]::IsNullOrWhiteSpace([string]$sbom.bomFormat)) { throw "invalid CycloneDX SBOM" }

Write-Host "[G6.3 4/8] Scan canonical image vulnerabilities with Trivy"
$trivyPath = Join-Path $artifactDir "trivy-vulnerabilities.json"
docker run --rm --pull=never -v /var/run/docker.sock:/var/run/docker.sock -v "$($artifactDir):/out" $trivyImage image --quiet --format json --output /out/trivy-vulnerabilities.json --severity HIGH,CRITICAL $image
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

if ($highVulns.Count -gt 0) {
    Write-Host ""
    Write-Host "Trivy HIGH vulnerability triage:"
    $highTriage = @(
        $highVulns | ForEach-Object {
            [pscustomobject]@{
                VulnerabilityID = [string]$_.VulnerabilityID
                PkgName = [string]$_.PkgName
                InstalledVersion = [string]$_.InstalledVersion
                FixedVersion = [string]$_.FixedVersion
                Title = [string]$_.Title
                PrimaryURL = [string]$_.PrimaryURL
            }
        } | Sort-Object PkgName, VulnerabilityID
    )
    $highTriage | Format-Table -AutoSize | Out-Host

    $fixableHigh = @($highTriage | Where-Object { -not [string]::IsNullOrWhiteSpace($_.FixedVersion) })
    $unfixedHigh = @($highTriage | Where-Object { [string]::IsNullOrWhiteSpace($_.FixedVersion) })

    Write-Host ""
    Write-Host "Trivy HIGH summary: total=$($highVulns.Count), fixable=$($fixableHigh.Count), no_fixed_version=$($unfixedHigh.Count)"

    if ($fixableHigh.Count -gt 0) {
        throw "SECURITY_FAIL: Trivy found $($fixableHigh.Count) HIGH vulnerability finding(s) with an available FixedVersion. Rebuild/remediate before G6.3 can pass."
    }
}

Write-Host "[G6.3 5/8] Scan clean Git snapshot for secrets with Gitleaks"
$repoPath = (Get-Location).Path
$gitRoot = (& git rev-parse --show-toplevel).Trim()
if ([string]::IsNullOrWhiteSpace($gitRoot)) { throw "Could not resolve Git repository root" }

$scanTemp = Join-Path $env:TEMP ("father-g6-gitleaks-" + [guid]::NewGuid().ToString("N"))
$scanZip = "$scanTemp.zip"
$scanExtract = Join-Path $scanTemp "extract"
New-Item -ItemType Directory -Force -Path $scanExtract | Out-Null

try {
    Write-Host "Create clean tracked-source snapshot from HEAD"
    & git -C $gitRoot archive --format=zip --output=$scanZip HEAD services/father-chassis
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $scanZip)) { throw "Could not create clean Git snapshot for secret scan" }

    Expand-Archive -Path $scanZip -DestinationPath $scanExtract -Force
    $scanTarget = Join-Path $scanExtract "services\father-chassis"
    if (-not (Test-Path $scanTarget)) { throw "Extracted Git snapshot does not contain services/father-chassis" }

    $gitleaksPath = Join-Path $artifactDir "gitleaks.json"
    docker run --rm --pull=never -v "$($scanTarget):/scan" -v "$($artifactDir):/out" $gitleaksImage dir /scan --report-format=json --report-path=/out/gitleaks.json --redact=100 --exit-code=0
    if ($LASTEXITCODE -ne 0) { throw "Gitleaks execution failed" }
}
finally {
    if (Test-Path $scanZip) { Remove-Item $scanZip -Force -ErrorAction SilentlyContinue }
    if (Test-Path $scanTemp) { Remove-Item $scanTemp -Recurse -Force -ErrorAction SilentlyContinue }
}

if (-not (Test-Path $gitleaksPath)) { "[]" | Set-Content -Encoding UTF8 $gitleaksPath }
$gitleaksRaw = Get-Content $gitleaksPath -Raw
$gitleaksParsed = $gitleaksRaw | ConvertFrom-Json
$gitleaks = @()
if ($null -ne $gitleaksParsed) {
    if ($gitleaksParsed -is [System.Array]) { $gitleaks = @($gitleaksParsed) }
    else { $gitleaks = @($gitleaksParsed) }
}

if ($gitleaks.Count -gt 0) {
    Write-Host ""
    Write-Host "Gitleaks findings (secret values are intentionally NOT printed):"
    foreach ($finding in $gitleaks) {
        [pscustomobject]@{
            RuleID = [string]$finding.RuleID
            Description = [string]$finding.Description
            File = [string]$finding.File
            StartLine = [string]$finding.StartLine
            EndLine = [string]$finding.EndLine
            Fingerprint = [string]$finding.Fingerprint
        } | Format-List | Out-Host
    }
    throw "SECURITY_FAIL: Gitleaks found $($gitleaks.Count) potential secret finding(s) in tracked source snapshot."
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

Write-Host "[G6.3 7/8] Run Semgrep SAST with local versioned rulepack"
$semgrepPath = Join-Path $artifactDir "semgrep.json"
$semgrepRules = Join-Path $repoPath "config\semgrep-g6.yml"
if (-not (Test-Path $semgrepRules)) { throw "Local Semgrep rulepack missing: $semgrepRules" }
docker run --rm --pull=never -v "$($repoPath):/src" $semgrepImage semgrep scan --config /src/config/semgrep-g6.yml --json --output /src/artifacts/security/semgrep.json /src/src/father
if ($LASTEXITCODE -ne 0) { throw "Semgrep execution failed" }
$semgrep = Read-JsonFile $semgrepPath
$semgrepResults = @($semgrep.results)
$semgrepErrors = @($semgrepResults | Where-Object { ([string]$_.extra.severity).ToUpperInvariant() -eq "ERROR" })
$semgrepWarnings = @($semgrepResults | Where-Object { ([string]$_.extra.severity).ToUpperInvariant() -eq "WARNING" })
$semgrepInfo = @($semgrepResults | Where-Object { ([string]$_.extra.severity).ToUpperInvariant() -eq "INFO" })

if ($semgrepResults.Count -gt 0) {
    Write-Host ""
    Write-Host "Semgrep findings:"
    foreach ($finding in $semgrepResults) {
        [pscustomobject]@{
            RuleID = [string]$finding.check_id
            Severity = [string]$finding.extra.severity
            Path = [string]$finding.path
            StartLine = [string]$finding.start.line
            EndLine = [string]$finding.end.line
            Message = [string]$finding.extra.message
        } | Format-List | Out-Host
    }
}

if ($semgrepErrors.Count -gt 0) {
    throw "SECURITY_FAIL: Semgrep found $($semgrepErrors.Count) ERROR finding(s)."
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
        high_fixable = if ($highVulns.Count -gt 0) { $fixableHigh.Count } else { 0 }
        high_without_fixed_version = if ($highVulns.Count -gt 0) { $unfixedHigh.Count } else { 0 }
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
        error = $semgrepErrors.Count
        warning = $semgrepWarnings.Count
        info = $semgrepInfo.Count
        total = $semgrepResults.Count
        report = "artifacts/security/semgrep.json"
    }
}

$summaryPath = Join-Path $artifactDir "g6_3_security_supply_chain_summary.json"
$result | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 $summaryPath

Write-Host ""
Write-Host "G6.3 SECURITY + SUPPLY CHAIN QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 12
