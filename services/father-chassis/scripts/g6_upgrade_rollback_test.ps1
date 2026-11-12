$ErrorActionPreference="Stop"
$base="http://localhost:8080"
$container="father-chassis-father-chassis-1"
$serviceImage="father-chassis-father-chassis:latest"
$rollbackTag="father-chassis-father-chassis:g6-rollback"

function Wait-Ready([int]$seconds=120){
    $deadline=(Get-Date).AddSeconds($seconds)
    do{
        try{
            $r=Invoke-RestMethod "$base/health/ready" -TimeoutSec 3
            if($r.ready){return $true}
        }catch{}
        Start-Sleep -Seconds 2
    }while((Get-Date)-lt $deadline)
    return $false
}

Write-Host "[G6.5] Capture and tag current image"
$before=docker inspect $container --format '{{.Image}}'
if($LASTEXITCODE -ne 0){throw "cannot read current image"}
docker image tag $before $rollbackTag
if($LASTEXITCODE -ne 0){throw "cannot tag rollback image"}

Write-Host "[G6.5] Rebuild current source as candidate"
docker compose build father-chassis
if($LASTEXITCODE -ne 0){throw "candidate build failed"}

Write-Host "[G6.5] Recreate candidate"
docker compose up -d --force-recreate father-chassis | Out-Null
$candidateReady=Wait-Ready
if(-not $candidateReady){throw "candidate not ready"}
$candidate=docker inspect $container --format '{{.Image}}'

Write-Host "[G6.5] Execute real rollback to previous image"
docker image tag $rollbackTag $serviceImage
if($LASTEXITCODE -ne 0){throw "cannot restore rollback tag"}

docker compose up -d --force-recreate --no-build father-chassis | Out-Null
$rollbackReady=Wait-Ready
if(-not $rollbackReady){throw "rollback image did not become ready"}
$afterRollback=docker inspect $container --format '{{.Image}}'

$rollbackRestored=($afterRollback -eq $before)

$result=[ordered]@{
 gate="G6.5_UPGRADE_ROLLBACK"
 previous_image=$before
 candidate_image=$candidate
 candidate_ready=$candidateReady
 rollback_executed=$true
 rollback_image=$afterRollback
 rollback_restored_previous_image=$rollbackRestored
 rollback_ready=$rollbackReady
 passed=($candidateReady -and $rollbackReady -and $rollbackRestored)
}
$result|ConvertTo-Json -Depth 10|Set-Content ".\artifacts\g6_upgrade_rollback.json"
$result|ConvertTo-Json -Depth 10
if(-not $result.passed){Write-Host "G6.5 UPGRADE/ROLLBACK: FAIL";exit 1}
Write-Host "G6.5 UPGRADE/ROLLBACK: PASS"
