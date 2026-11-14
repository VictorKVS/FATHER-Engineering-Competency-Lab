param()
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $serviceDir "scripts\brain_storage_bench_p0_smoke.ps1"
$artifactDir = Join-Path $serviceDir "artifacts\local\brain-storage-bench"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null
$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$summaryPath = Join-Path $artifactDir ("P0B_runtime_summary_" + $date + ".json")

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

  & $runner $candidate
  $exitCode = $LASTEXITCODE

  $after = Get-ChildItem $artifactDir -Filter ("P0B_runtime_smoke_" + $candidate + "_*.json") -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  if($null -eq $after -or ($null -ne $before -and $after.FullName -eq $before.FullName)){
    $results += [ordered]@{
      candidate=$candidate
      status="NO_EVIDENCE"
      exit_code=$exitCode
      passed=$false
    }
    continue
  }

  $payload = Get-Content $after.FullName -Raw | ConvertFrom-Json
  $results += [ordered]@{
    candidate=$candidate
    status=$payload.status
    image=$payload.image
    image_id=$payload.image_id
    runtime_startup_seconds=$payload.runtime_startup_seconds
    functional_smoke=$payload.functional_smoke
    cpu_percent=$payload.cpu_percent
    memory_usage=$payload.memory_usage
    memory_percent=$payload.memory_percent
    network_io=$payload.network_io
    block_io=$payload.block_io
    evidence_path=$after.FullName
    exit_code=$exitCode
    passed=[bool]$payload.passed
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
  Select-Object candidate,status,runtime_startup_seconds,memory_usage,cpu_percent,functional_smoke |
  Format-Table -AutoSize

if(-not $summary.passed){ exit 1 }
