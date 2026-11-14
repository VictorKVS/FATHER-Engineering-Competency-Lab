param()
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $serviceDir "scripts\brain_storage_bench_p0_smoke.ps1"
$artifactDir = Join-Path $serviceDir "artifacts\local\brain-storage-bench"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null
$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$summaryPath = Join-Path $artifactDir ("P0B_runtime_summary_" + $date + ".json")

function Get-OptionalProperty {
  param(
    [Parameter(Mandatory=$true)]$Object,
    [Parameter(Mandatory=$true)][string]$Name
  )
  $property = $Object.PSObject.Properties[$Name]
  if($null -eq $property){ return $null }
  return $property.Value
}

$candidates = @("postgres","pgvector","qdrant","neo4j","opensearch")
$results = @()

foreach($candidate in $candidates){
  Write-Host ""
  Write-Host "============================================================"
  Write-Host "[P0B] Runtime smoke: $candidate"
  Write-Host "============================================================"

  $before = Get-ChildItem $artifactDir -Filter ("P0B_runtime_smoke_" + $candidate + "_*.json") -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  $child = Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy","Bypass",
    "-File",$runner,
    $candidate
  ) -Wait -PassThru -NoNewWindow
  $exitCode = $child.ExitCode

  $after = Get-ChildItem $artifactDir -Filter ("P0B_runtime_smoke_" + $candidate + "_*.json") -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  if($null -eq $after -or ($null -ne $before -and $after.FullName -eq $before.FullName)){
    $results += [ordered]@{
      candidate=$candidate
      status="NO_EVIDENCE"
      reason="runner produced no new evidence file"
      exit_code=$exitCode
      passed=$false
    }
    continue
  }

  $payload = Get-Content $after.FullName -Raw | ConvertFrom-Json
  $results += [ordered]@{
    candidate=$candidate
    status=Get-OptionalProperty $payload "status"
    reason=Get-OptionalProperty $payload "reason"
    image=Get-OptionalProperty $payload "image"
    image_id=Get-OptionalProperty $payload "image_id"
    runtime_startup_seconds=Get-OptionalProperty $payload "runtime_startup_seconds"
    functional_smoke=Get-OptionalProperty $payload "functional_smoke"
    cpu_percent=Get-OptionalProperty $payload "cpu_percent"
    memory_usage=Get-OptionalProperty $payload "memory_usage"
    memory_percent=Get-OptionalProperty $payload "memory_percent"
    network_io=Get-OptionalProperty $payload "network_io"
    block_io=Get-OptionalProperty $payload "block_io"
    evidence_path=$after.FullName
    exit_code=$exitCode
    passed=[bool](Get-OptionalProperty $payload "passed")
  }
}

$summary=[ordered]@{
  qualification="BRAIN_STORAGE_BENCH_P0B_RUNTIME_BATCH"
  timestamp_utc=(Get-Date).ToUniversalTime().ToString("o")
  results=$results
  pass_count=@($results | Where-Object {$_.passed}).Count
  fail_count=@($results | Where-Object {-not $_.passed}).Count
  passed=(@($results | Where-Object {-not $_.passed}).Count -eq 0)
}

$summary | ConvertTo-Json -Depth 10 | Set-Content -Path $summaryPath -Encoding UTF8
$summary | ConvertTo-Json -Depth 10
Write-Host ""
Write-Host "Summary evidence: $summaryPath"

Write-Host ""
Write-Host "P0B TABLE"
$results |
  Select-Object candidate,status,runtime_startup_seconds,memory_usage,cpu_percent,functional_smoke,reason |
  Format-Table -AutoSize

if(-not $summary.passed){ exit 1 }
