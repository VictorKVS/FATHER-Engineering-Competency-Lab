param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $serviceDir "..\..")).Path
$trustDir = Join-Path $repoRoot "projects\FATHER-TRUST-COMPETENCY-0001"
$artifactDir = Join-Path $serviceDir "artifacts"
$artifactPath = Join-Path $artifactDir "g7_factory_preflight_summary.json"

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )
    Write-Host "[G7 PRECHECK] $Name"
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$started = (Get-Date).ToUniversalTime()
$result = [ordered]@{
    qualification = "G7_FACTORY_PREFLIGHT"
    started_at_utc = $started.ToString("o")
    chassis_compile = $false
    chassis_tests = $false
    trust_compile = $false
    trust_tests = $false
    product_recipe_smoke = $false
    passed = $false
}

try {
    Push-Location $serviceDir
    try {
        Invoke-Step "Compile father-chassis sources/tests" {
            & $Python -m compileall -q src tests
        }
        $result.chassis_compile = $true

        Invoke-Step "Run father-chassis pytest" {
            & $Python -m pytest -q
        }
        $result.chassis_tests = $true

        Invoke-Step "Product Recipe smoke" {
            $env:PYTHONPATH = (Join-Path $serviceDir "src")
            @'
from father.factory.block_catalog import build_reference_block_catalog
from father.factory.product_recipe import ProductRecipeBuilder
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner

req = CustomerRequirement(
    requirement_id="REQ-G7-PREFLIGHT",
    title="G7 preflight knowledge product",
    needs=frozenset({"analyze_documents", "create_report", "enforce_policy", "run_workflow"}),
    metadata={"agent_id": "g7-preflight-agent"},
)
plan = ProductRecipeBuilder(
    RequirementPlanner(),
    build_reference_block_catalog(),
).plan(req, product_id="PRD-G7-PREFLIGHT")
assert plan.buildable
assert plan.recipe is not None
assert plan.recipe.recipe_hash
print(plan.recipe.recipe_hash)
'@ | & $Python -
        }
        $result.product_recipe_smoke = $true
    }
    finally {
        Pop-Location
    }

    Push-Location $trustDir
    try {
        Invoke-Step "Compile Trust & Competency sources/tests" {
            & $Python -m compileall -q src tests
        }
        $result.trust_compile = $true

        Invoke-Step "Run Trust & Competency pytest" {
            & $Python -m pytest -q
        }
        $result.trust_tests = $true
    }
    finally {
        Pop-Location
    }

    $result.passed = (
        $result.chassis_compile -and
        $result.chassis_tests -and
        $result.trust_compile -and
        $result.trust_tests -and
        $result.product_recipe_smoke
    )
}
catch {
    $result.error = $_.Exception.Message
}
finally {
    $result.completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    $result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
}

if (-not $result.passed) {
    Write-Host ""
    Write-Host "G7 FACTORY PREFLIGHT: FAIL"
    $result | ConvertTo-Json -Depth 10
    exit 1
}

Write-Host ""
Write-Host "G7 FACTORY PREFLIGHT: PASS"
$result | ConvertTo-Json -Depth 10
exit 0
