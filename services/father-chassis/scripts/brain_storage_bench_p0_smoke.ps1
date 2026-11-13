param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("postgres","pgvector","qdrant","neo4j","opensearch")]
  [string]$Candidate
)
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$compose = Join-Path $serviceDir "benchmarks\brain-storage\compose.yaml"
$artifactDir = Join-Path $serviceDir "artifacts\local\brain-storage-bench"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null
$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$out = Join-Path $artifactDir ("P0_smoke_" + $Candidate + "_" + $date + ".json")

$container = "father-bench-$Candidate"
$start = Get-Date
$dockerReady=$false
$started=$false

try {
  try {
    $serverVersion = docker version --format '{{.Server.Version}}' 2>$null
    if($LASTEXITCODE -eq 0 -and $serverVersion){ $dockerReady=$true }
  } catch {}

  if(-not $dockerReady){
    $blocked=[ordered]@{
      qualification="BRAIN_STORAGE_BENCH_P0_SMOKE"
      candidate=$Candidate
      status="ENVIRONMENT_BLOCKED"
      reason="Docker Engine is not available"
      started_at_utc=$start.ToUniversalTime().ToString("o")
      passed=$false
    }
    $blocked | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
    $blocked | ConvertTo-Json -Depth 8
    Write-Host "Evidence: $out"
    exit 2
  }

  docker compose -f $compose --profile $Candidate up -d $Candidate
  if($LASTEXITCODE -ne 0){ throw "docker compose up failed" }
  $started=$true

  $deadline=(Get-Date).AddSeconds(90)
  $ready=$false
  while((Get-Date) -lt $deadline -and -not $ready){
    Start-Sleep -Seconds 2
    switch($Candidate){
      "postgres" {
        docker exec $container pg_isready -U father -d father_bench *> $null
        $ready=($LASTEXITCODE -eq 0)
      }
      "pgvector" {
        docker exec $container pg_isready -U father -d father_bench *> $null
        $ready=($LASTEXITCODE -eq 0)
      }
      "qdrant" {
        try { Invoke-RestMethod -Uri "http://127.0.0.1:56333/" -TimeoutSec 3 | Out-Null; $ready=$true } catch {}
      }
      "neo4j" {
        docker exec $container cypher-shell -u neo4j -p father_bench_2026 "RETURN 1;" *> $null
        $ready=($LASTEXITCODE -eq 0)
      }
      "opensearch" {
        try { Invoke-RestMethod -Uri "http://127.0.0.1:59200/" -TimeoutSec 3 | Out-Null; $ready=$true } catch {}
      }
    }
  }
  if(-not $ready){ throw "candidate did not become ready in 90 seconds" }

  $functional=$false
  switch($Candidate){
    "postgres" {
      docker exec $container psql -U father -d father_bench -c "CREATE TABLE IF NOT EXISTS smoke(id int primary key, value text); INSERT INTO smoke VALUES(1,'ok') ON CONFLICT(id) DO UPDATE SET value='ok'; SELECT value FROM smoke WHERE id=1;" *> $null
      $functional=($LASTEXITCODE -eq 0)
    }
    "pgvector" {
      docker exec $container psql -U father -d father_bench -c "CREATE EXTENSION IF NOT EXISTS vector; CREATE TABLE IF NOT EXISTS smoke(id int primary key, v vector(3)); INSERT INTO smoke VALUES(1,'[1,2,3]') ON CONFLICT(id) DO UPDATE SET v='[1,2,3]'; SELECT id FROM smoke ORDER BY v <-> '[1,2,3]' LIMIT 1;" *> $null
      $functional=($LASTEXITCODE -eq 0)
    }
    "qdrant" {
      $body='{"vectors":{"size":3,"distance":"Cosine"}}'
      try {
        Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:56333/collections/smoke" -ContentType "application/json" -Body $body | Out-Null
        $functional=$true
      } catch {}
    }
    "neo4j" {
      docker exec $container cypher-shell -u neo4j -p father_bench_2026 "MERGE (n:Smoke {id:1}) SET n.value='ok' RETURN n.value;" *> $null
      $functional=($LASTEXITCODE -eq 0)
    }
    "opensearch" {
      try {
        Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:59200/smoke" -ContentType "application/json" -Body '{"settings":{"number_of_shards":1,"number_of_replicas":0}}' | Out-Null
        Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:59200/smoke/_doc/1?refresh=true" -ContentType "application/json" -Body '{"value":"ok"}' | Out-Null
        $functional=$true
      } catch {}
    }
  }

  $inspect = docker inspect $container | ConvertFrom-Json
  $statsRaw = docker stats $container --no-stream --format '{{json .}}'
  $stats = $statsRaw | ConvertFrom-Json

  $result=[ordered]@{
    qualification="BRAIN_STORAGE_BENCH_P0_SMOKE"
    candidate=$Candidate
    status=if($ready -and $functional){"PASS"}else{"FAIL"}
    image=$inspect[0].Config.Image
    image_id=$inspect[0].Image
    started_at_utc=$start.ToUniversalTime().ToString("o")
    ready_at_utc=(Get-Date).ToUniversalTime().ToString("o")
    startup_seconds=[math]::Round(((Get-Date)-$start).TotalSeconds,3)
    functional_smoke=$functional
    cpu_percent=$stats.CPUPerc
    memory_usage=$stats.MemUsage
    memory_percent=$stats.MemPerc
    network_io=$stats.NetIO
    block_io=$stats.BlockIO
    passed=($ready -and $functional)
  }
  $result | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
  $result | ConvertTo-Json -Depth 8
  Write-Host "Evidence: $out"
  if(-not $result.passed){ exit 1 }
}
catch {
  $failed=[ordered]@{
    qualification="BRAIN_STORAGE_BENCH_P0_SMOKE"
    candidate=$Candidate
    status="FAIL"
    reason=$_.Exception.Message
    started_at_utc=$start.ToUniversalTime().ToString("o")
    completed_at_utc=(Get-Date).ToUniversalTime().ToString("o")
    passed=$false
  }
  $failed | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
  $failed | ConvertTo-Json -Depth 8
  Write-Host "Evidence: $out"
  exit 1
}
finally {
  if($started -and $dockerReady){
    try {
      docker compose -f $compose --profile $Candidate down -v --remove-orphans *> $null
    } catch {}
  }
}
