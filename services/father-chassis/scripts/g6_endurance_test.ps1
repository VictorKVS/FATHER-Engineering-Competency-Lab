param([int]$Minutes=5)
$ErrorActionPreference="Stop"
$base="http://localhost:8080"
$end=(Get-Date).AddMinutes($Minutes)
$checks=0
$failures=0
$maxMs=0.0
Write-Host "[G6.6] Endurance for $Minutes minute(s)"
do{
 $sw=[Diagnostics.Stopwatch]::StartNew()
 try{
   $r=Invoke-RestMethod "$base/health/ready" -TimeoutSec 5
   if(-not $r.ready){throw "not ready"}
 }catch{$failures++}
 $sw.Stop()
 if($sw.Elapsed.TotalMilliseconds -gt $maxMs){$maxMs=$sw.Elapsed.TotalMilliseconds}
 $checks++
 Start-Sleep -Seconds 5
}while((Get-Date)-lt $end)

$result=[ordered]@{
 gate="G6.6_ENDURANCE"
 duration_minutes=$Minutes
 checks=$checks
 failures=$failures
 max_ready_latency_ms=[Math]::Round($maxMs,2)
 passed=($failures -eq 0)
}
$result|ConvertTo-Json -Depth 10|Set-Content ".\artifacts\g6_endurance.json"
$result|ConvertTo-Json -Depth 10
if(-not $result.passed){Write-Host "G6.6 ENDURANCE: FAIL";exit 1}
Write-Host "G6.6 ENDURANCE: PASS"
