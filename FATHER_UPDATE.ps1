param(
    [string]$RepoRoot = "G:\1\FATHER-Engineering-Competency-Lab"
)

$ErrorActionPreference = "Stop"

Write-Host "=== FATHER GITHUB UPDATE / RUN ===" -ForegroundColor Cyan

if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
    throw "Git repository not found: $RepoRoot"
}

$Service = Join-Path $RepoRoot "services\father-controller"

Write-Host "[1/4] Fetch origin/main" -ForegroundColor Yellow
git -C $RepoRoot fetch origin main
if ($LASTEXITCODE -ne 0) { throw "git fetch origin main failed" }

Write-Host "[2/4] Sync father-controller from origin/main" -ForegroundColor Yellow
git -C $RepoRoot checkout origin/main -- services/father-controller
if ($LASTEXITCODE -ne 0) { throw "controller sync from origin/main failed" }

New-Item -ItemType Directory -Path (Join-Path $Service "data") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Service "evidence") -Force | Out-Null

Write-Host "[3/4] Select newest Stage" -ForegroundColor Yellow
$Runner = Get-ChildItem $Service -Filter "RUN_FATHER_STAGE*.ps1" -File |
    Sort-Object {
        if ($_.BaseName -match 'STAGE(\d+)') { [int]$Matches[1] } else { 0 }
    } -Descending |
    Select-Object -First 1

if (-not $Runner) { throw "No Stage runner found" }

Write-Host "RUNNER: $($Runner.Name)" -ForegroundColor Green

Write-Host "[4/4] Run latest Stage" -ForegroundColor Yellow
Set-Location $Service
& $Runner.FullName
if ($LASTEXITCODE -ne 0) { throw "FATHER Stage failed" }

Write-Host "=== FATHER GITHUB UPDATE COMPLETE ===" -ForegroundColor Green
