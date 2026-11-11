$ErrorActionPreference = "Stop"

function Run-Step($name, $script) {
    Write-Host "`n==== $name ===="
    & powershell -ExecutionPolicy Bypass -File $script
    if ($LASTEXITCODE -ne 0) { throw "$name failed with exit code $LASTEXITCODE" }
}

Run-Step "ENVIRONMENT CHECK" ".\scripts\check_env.ps1"
Run-Step "START / COLD START" ".\scripts\start_local.ps1"
Run-Step "SMOKE TEST" ".\scripts\smoke_test.ps1"
Run-Step "RECOVERY TEST" ".\scripts\recovery_test.ps1"

if ($env:FATHER_SKIP_REAL_LLM -eq "1") {
    Write-Host "`n[WARN] Real LLM qualification skipped by FATHER_SKIP_REAL_LLM=1"
} else {
    Run-Step "LOCAL LLM QUALIFICATION" ".\scripts\llm_test.ps1"
}

Run-Step "OSINT PRODUCT QUALIFICATION" ".\scripts\osint_product_test.ps1"
Write-Host "`nFATHER FACTORY 1.0 RC QUALIFICATION: PASS"
