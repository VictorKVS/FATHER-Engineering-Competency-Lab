$ErrorActionPreference = "Stop"
$fail = @()

Write-Host "[G6.4] Dependency integrity / canonical source provenance"

$images = @(
    "python:3.12-slim",
    "pgvector/pgvector:pg16",
    "redis:7-alpine"
)

$inventory = @()
foreach ($img in $images) {
    docker image inspect $img *> $null
    if ($LASTEXITCODE -ne 0) {
        $fail += "missing_image:$img"
        continue
    }

    $id = docker image inspect $img --format '{{.Id}}'
    $digests = docker image inspect $img --format '{{json .RepoDigests}}'

    if ([string]::IsNullOrWhiteSpace($digests) -or $digests -eq "null") {
        $fail += "missing_digest:$img"
    }

    $inventory += [ordered]@{
        image = $img
        id = $id
        repo_digests = $digests
    }
}

Write-Host "[G6.4] Git provenance"
$head = (git rev-parse HEAD).Trim()
$branchName = (git branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($head)) {
    $fail += "git_head_unavailable"
}

# Scope cleanliness to the canonical chassis only.
# G6 evidence JSON files are expected runtime outputs and are explicitly allowed.
$rawStatus = @(git status --porcelain --untracked-files=all -- services/father-chassis)
$unexpected = @()

foreach ($entry in $rawStatus) {
    $normalized = $entry.Trim()

    if ($normalized -match '^\?\? services/father-chassis/artifacts/g6_.*\.json$') {
        continue
    }

    if (-not [string]::IsNullOrWhiteSpace($normalized)) {
        $unexpected += $normalized
    }
}

$canonicalClean = ($unexpected.Count -eq 0)
if (-not $canonicalClean) {
    $fail += "canonical_chassis_dirty"
}

$result = [ordered]@{
    gate = "G6.4_SUPPLY_CHAIN"
    git_branch = $branchName
    git_head = $head
    canonical_path = "services/father-chassis"
    images = $inventory
    canonical_source_clean = $canonicalClean
    unexpected_entries = $unexpected
    ignored_expected_evidence = @(
        "services/father-chassis/artifacts/g6_*.json"
    )
    failures = $fail
    passed = ($fail.Count -eq 0)
}

$result | ConvertTo-Json -Depth 10 | Set-Content ".\artifacts\g6_supply_chain.json"
$result | ConvertTo-Json -Depth 10

if (-not $result.passed) {
    Write-Host "G6.4 SUPPLY CHAIN: FAIL"
    exit 1
}

Write-Host "G6.4 SUPPLY CHAIN: PASS"
