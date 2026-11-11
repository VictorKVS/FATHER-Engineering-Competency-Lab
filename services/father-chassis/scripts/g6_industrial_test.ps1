param([int]$EnduranceMinutes=5)
$ErrorActionPreference="Stop"

function Run-Gate($name,$script,$args=@()) {
 Write-Host ""
 Write-Host "========== $name =========="
 & powershell -ExecutionPolicy Bypass -File $script @args
 if($LASTEXITCODE -ne 0){ throw "$name failed with exit code $LASTEXITCODE" }
}

New-Item -ItemType Directory -Force ".\artifacts" | Out-Null
Run-Gate "G6.1 LOAD" ".\scripts\g6_load_test.ps1"
Run-Gate "G6.2 CHAOS" ".\scripts\g6_chaos_test.ps1"
Run-Gate "G6.3 SECURITY" ".\scripts\g6_security_test.ps1"
Run-Gate "G6.4 SUPPLY CHAIN" ".\scripts\g6_supply_chain_test.ps1"
Run-Gate "G6.5 UPGRADE / ROLLBACK" ".\scripts\g6_upgrade_rollback_test.ps1"
Run-Gate "G6.6 ENDURANCE" ".\scripts\g6_endurance_test.ps1" @("-Minutes",$EnduranceMinutes)

$files=@(
 ".\artifacts\g6_load.json",
 ".\artifacts\g6_chaos.json",
 ".\artifacts\g6_security.json",
 ".\artifacts\g6_supply_chain.json",
 ".\artifacts\g6_upgrade_rollback.json",
 ".\artifacts\g6_endurance.json"
)
$gates=@()
foreach($f in $files){$gates += (Get-Content $f -Raw | ConvertFrom-Json)}
$report=[ordered]@{
 qualification="FATHER_G6_INDUSTRIAL"
 generated_at=(Get-Date).ToUniversalTime().ToString("o")
 gates=$gates
 passed=(@($gates|Where-Object{-not $_.passed}).Count -eq 0)
}
$report|ConvertTo-Json -Depth 20|Set-Content ".\artifacts\g6_industrial_report.json"
$report|ConvertTo-Json -Depth 20
if(-not $report.passed){Write-Host "FATHER G6 INDUSTRIAL: FAIL";exit 1}
Write-Host ""
Write-Host "FATHER G6 INDUSTRIAL: PASS"
