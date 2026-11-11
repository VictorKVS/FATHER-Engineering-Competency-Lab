$ErrorActionPreference = "Stop"
$base="http://localhost:8080"

Write-Host "[G6.2] Seed persistent marker"
$marker="G6-CHAOS-" + [guid]::NewGuid().ToString()
$body=@{source="g6-chaos";text=$marker} | ConvertTo-Json
Invoke-RestMethod "$base/ingest" -Method Post -ContentType "application/json" -Body $body | Out-Null

Write-Host "[G6.2] Kill API container"
docker compose kill father-chassis | Out-Null
Start-Sleep -Seconds 2

Write-Host "[G6.2] Recover API container"
docker compose up -d father-chassis | Out-Null
$deadline=(Get-Date).AddMinutes(2)
$ready=$false
do {
    try {
        $r=Invoke-RestMethod "$base/health/ready" -TimeoutSec 3
        if ($r.ready) { $ready=$true; break }
    } catch {}
    Start-Sleep -Seconds 2
} while((Get-Date)-lt $deadline)
if (-not $ready) { throw "API did not recover after kill" }

Write-Host "[G6.2] Verify persistence after forced kill"
$q=@{input=$marker}|ConvertTo-Json
$res=Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $q
$persisted=($res.evidence.Count -ge 1)

$result=[ordered]@{
 gate="G6.2_CHAOS"
 forced_kill=$true
 recovered=$ready
 persistence_after_kill=$persisted
 passed=($ready -and $persisted)
}
$result|ConvertTo-Json -Depth 10|Set-Content ".\artifacts\g6_chaos.json"
$result|ConvertTo-Json -Depth 10
if(-not $result.passed){Write-Host "G6.2 CHAOS: FAIL";exit 1}
Write-Host "G6.2 CHAOS: PASS"
