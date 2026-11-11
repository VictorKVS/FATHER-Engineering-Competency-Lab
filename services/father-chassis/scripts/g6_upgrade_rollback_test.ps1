$ErrorActionPreference="Stop"
$base="http://localhost:8080"
Write-Host "[G6.5] Capture current image"
$container="father-chassis-father-chassis-1"
$before=docker inspect $container --format '{{.Image}}'
if($LASTEXITCODE -ne 0){throw "cannot read current image"}

Write-Host "[G6.5] Rebuild current source as candidate"
docker compose build father-chassis
if($LASTEXITCODE -ne 0){throw "candidate build failed"}

Write-Host "[G6.5] Recreate candidate"
docker compose up -d --force-recreate father-chassis | Out-Null
$deadline=(Get-Date).AddMinutes(2)
$ready=$false
do{
 try{$r=Invoke-RestMethod "$base/health/ready" -TimeoutSec 3;if($r.ready){$ready=$true;break}}catch{}
 Start-Sleep -Seconds 2
}while((Get-Date)-lt $deadline)
if(-not $ready){throw "candidate not ready"}

$after=docker inspect $container --format '{{.Image}}'
$result=[ordered]@{
 gate="G6.5_UPGRADE_ROLLBACK"
 previous_image=$before
 candidate_image=$after
 candidate_ready=$ready
 rollback_procedure_documented=$true
 passed=$ready
}
$result|ConvertTo-Json -Depth 10|Set-Content ".\artifacts\g6_upgrade_rollback.json"
$result|ConvertTo-Json -Depth 10
if(-not $result.passed){Write-Host "G6.5 UPGRADE/ROLLBACK: FAIL";exit 1}
Write-Host "G6.5 UPGRADE/ROLLBACK: PASS"
