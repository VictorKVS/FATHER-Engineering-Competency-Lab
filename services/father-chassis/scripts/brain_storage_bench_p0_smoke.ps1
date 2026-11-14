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
$out = Join-Path $artifactDir ("P0B_runtime_smoke_" + $Candidate + "_" + $date + ".json")

function Invoke-NativeExit {
  param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [Parameter(Mandatory=$true)][string[]]$Arguments
  )
  $previousPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    $lines = & $FilePath @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    [pscustomobject]@{
      ExitCode = $exitCode
      Output = ($lines | Out-String).Trim()
    }
  }
  finally {
    $ErrorActionPreference = $previousPreference
  }
}

function Get-ContainerDiagnostics {
  param([string]$Container)
  $inspectResult = Invoke-NativeExit -FilePath "docker" -Arguments @("inspect",$Container)
  $logsResult = Invoke-NativeExit -FilePath "docker" -Arguments @("logs","--tail","120",$Container)

  $state = $null
  $exitCode = $null
  $oomKilled = $null
  if($inspectResult.ExitCode -eq 0){
    try {
      $inspect = $inspectResult.Output | ConvertFrom-Json
      $state = $inspect[0].State.Status
      $exitCode = $inspect[0].State.ExitCode
      $oomKilled = $inspect[0].State.OOMKilled
    } catch {}
  }

  [ordered]@{
    container_state=$state
    container_exit_code=$exitCode
    oom_killed=$oomKilled
    logs_tail=$logsResult.Output
  }
}

$images=[ordered]@{
  postgres="postgres:18-alpine"
  pgvector="pgvector/pgvector:0.8.7-pg18-trixie"
  qdrant="qdrant/qdrant:latest"
  neo4j="neo4j:2026.10.2"
  opensearch="opensearchproject/opensearch:3.9.0"
}

$container = "father-bench-$Candidate"
$image = $images[$Candidate]
$dockerReady=$false
$started=$false
$start=$null

try {
  $server = Invoke-NativeExit -FilePath "docker" -Arguments @("version","--format","{{.Server.Version}}")
  if($server.ExitCode -eq 0 -and $server.Output){ $dockerReady=$true }

  if(-not $dockerReady){
    $blocked=[ordered]@{
      qualification="BRAIN_STORAGE_BENCH_P0B_RUNTIME_SMOKE"
      candidate=$Candidate
      status="ENVIRONMENT_BLOCKED"
      reason="Docker Engine is not available"
      passed=$false
    }
    $blocked | ConvertTo-Json -Depth 10 | Set-Content -Path $out -Encoding UTF8
    $blocked | ConvertTo-Json -Depth 10
    Write-Host "Evidence: $out"
    exit 2
  }

  $imageInspect = Invoke-NativeExit -FilePath "docker" -Arguments @("image","inspect",$image)
  if($imageInspect.ExitCode -ne 0){
    $blocked=[ordered]@{
      qualification="BRAIN_STORAGE_BENCH_P0B_RUNTIME_SMOKE"
      candidate=$Candidate
      image=$image
      status="IMAGE_NOT_PREPARED"
      reason="Run brain_storage_bench_prepare_images.ps1 first; runtime benchmark never includes image pull time"
      passed=$false
    }
    $blocked | ConvertTo-Json -Depth 10 | Set-Content -Path $out -Encoding UTF8
    $blocked | ConvertTo-Json -Depth 10
    Write-Host "Evidence: $out"
    exit 2
  }

  if($Candidate -eq "opensearch"){
    $sysctl = Invoke-NativeExit -FilePath "wsl.exe" -Arguments @("-d","docker-desktop","sh","-lc","sysctl -n vm.max_map_count")
    $mapCount = 0
    [void][int]::TryParse($sysctl.Output.Trim(), [ref]$mapCount)
    if($sysctl.ExitCode -ne 0 -or $mapCount -lt 262144){
      $blocked=[ordered]@{
        qualification="BRAIN_STORAGE_BENCH_P0B_RUNTIME_SMOKE"
        candidate=$Candidate
        image=$image
        status="ENVIRONMENT_BLOCKED"
        reason="OpenSearch requires vm.max_map_count >= 262144 in docker-desktop WSL"
        observed_vm_max_map_count=$mapCount
        required_vm_max_map_count=262144
        passed=$false
      }
      $blocked | ConvertTo-Json -Depth 10 | Set-Content -Path $out -Encoding UTF8
      $blocked | ConvertTo-Json -Depth 10
      Write-Host "Evidence: $out"
      exit 2
    }
  }

  $start = Get-Date
  $up = Invoke-NativeExit -FilePath "docker" -Arguments @(
    "compose","-f",$compose,"--profile",$Candidate,
    "up","-d","--pull","never",$Candidate
  )
  if($up.ExitCode -ne 0){ throw "docker compose up failed: $($up.Output)" }
  $started=$true

  $timeoutSeconds = if($Candidate -eq "opensearch"){180}else{90}
  $deadline=(Get-Date).AddSeconds($timeoutSeconds)
  $ready=$false
  $lastProbe=""

  while((Get-Date) -lt $deadline -and -not $ready){
    Start-Sleep -Milliseconds 750

    $stateProbe = Invoke-NativeExit -FilePath "docker" -Arguments @("inspect","-f","{{.State.Status}}",$container)
    if($stateProbe.ExitCode -ne 0){
      $lastProbe=$stateProbe.Output
      continue
    }
    if($stateProbe.Output.Trim() -eq "exited" -or $stateProbe.Output.Trim() -eq "dead"){
      break
    }

    switch($Candidate){
      "postgres" {
        $probe=Invoke-NativeExit -FilePath "docker" -Arguments @(
          "exec",$container,"pg_isready","-U","father","-d","father_bench"
        )
        $ready=($probe.ExitCode -eq 0)
        $lastProbe=$probe.Output
      }
      "pgvector" {
        $probe=Invoke-NativeExit -FilePath "docker" -Arguments @(
          "exec",$container,"pg_isready","-U","father","-d","father_bench"
        )
        $ready=($probe.ExitCode -eq 0)
        $lastProbe=$probe.Output
      }
      "qdrant" {
        try {
          Invoke-RestMethod -Uri "http://127.0.0.1:56333/" -TimeoutSec 2 | Out-Null
          $ready=$true
        } catch { $lastProbe=$_.Exception.Message }
      }
      "neo4j" {
        $probe=Invoke-NativeExit -FilePath "docker" -Arguments @(
          "exec",$container,"cypher-shell","-u","neo4j","-p","father_bench_2026","RETURN 1;"
        )
        $ready=($probe.ExitCode -eq 0)
        $lastProbe=$probe.Output
      }
      "opensearch" {
        try {
          Invoke-RestMethod -Uri "http://127.0.0.1:59200/" -TimeoutSec 2 | Out-Null
          $ready=$true
        } catch { $lastProbe=$_.Exception.Message }
      }
    }
  }

  $readyAt=Get-Date
  if(-not $ready){
    $diag = Get-ContainerDiagnostics -Container $container
    $failure=[ordered]@{
      qualification="BRAIN_STORAGE_BENCH_P0B_RUNTIME_SMOKE"
      candidate=$Candidate
      image=$image
      status="READINESS_FAILED"
      reason="candidate did not become ready in $timeoutSeconds seconds"
      last_probe=$lastProbe
      runtime_wait_seconds=[math]::Round(($readyAt-$start).TotalSeconds,3)
      container_state=$diag.container_state
      container_exit_code=$diag.container_exit_code
      oom_killed=$diag.oom_killed
      logs_tail=$diag.logs_tail
      passed=$false
    }
    $failure | ConvertTo-Json -Depth 10 | Set-Content -Path $out -Encoding UTF8
    $failure | ConvertTo-Json -Depth 10
    Write-Host "Evidence: $out"
    exit 1
  }

  $functional=$false
  switch($Candidate){
    "postgres" {
      $probe=Invoke-NativeExit -FilePath "docker" -Arguments @(
        "exec",$container,"psql","-U","father","-d","father_bench","-c",
        "CREATE TABLE IF NOT EXISTS smoke(id int primary key, value text); INSERT INTO smoke VALUES(1,'ok') ON CONFLICT(id) DO UPDATE SET value='ok'; SELECT value FROM smoke WHERE id=1;"
      )
      $functional=($probe.ExitCode -eq 0)
    }
    "pgvector" {
      $probe=Invoke-NativeExit -FilePath "docker" -Arguments @(
        "exec",$container,"psql","-U","father","-d","father_bench","-c",
        "CREATE EXTENSION IF NOT EXISTS vector; CREATE TABLE IF NOT EXISTS smoke(id int primary key, v vector(3)); INSERT INTO smoke VALUES(1,'[1,2,3]') ON CONFLICT(id) DO UPDATE SET v='[1,2,3]'; SELECT id FROM smoke ORDER BY v <-> '[1,2,3]' LIMIT 1;"
      )
      $functional=($probe.ExitCode -eq 0)
    }
    "qdrant" {
      $body='{"vectors":{"size":3,"distance":"Cosine"}}'
      try {
        Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:56333/collections/smoke" -ContentType "application/json" -Body $body | Out-Null
        $functional=$true
      } catch {}
    }
    "neo4j" {
      $probe=Invoke-NativeExit -FilePath "docker" -Arguments @(
        "exec",$container,"cypher-shell","-u","neo4j","-p","father_bench_2026",
        "MERGE (n:Smoke {id:1}) SET n.value='ok' RETURN n.value;"
      )
      $functional=($probe.ExitCode -eq 0)
    }
    "opensearch" {
      try {
        Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:59200/smoke" -ContentType "application/json" -Body '{"settings":{"number_of_shards":1,"number_of_replicas":0}}' | Out-Null
        Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:59200/smoke/_doc/1?refresh=true" -ContentType "application/json" -Body '{"value":"ok"}' | Out-Null
        $functional=$true
      } catch {}
    }
  }

  Start-Sleep -Seconds 1
  $inspect = (Invoke-NativeExit -FilePath "docker" -Arguments @("inspect",$container)).Output | ConvertFrom-Json
  $stats = (Invoke-NativeExit -FilePath "docker" -Arguments @(
    "stats",$container,"--no-stream","--format","{{json .}}"
  )).Output | ConvertFrom-Json

  $result=[ordered]@{
    qualification="BRAIN_STORAGE_BENCH_P0B_RUNTIME_SMOKE"
    candidate=$Candidate
    status=if($ready -and $functional){"PASS"}else{"FUNCTIONAL_FAIL"}
    image=$inspect[0].Config.Image
    image_id=$inspect[0].Image
    started_at_utc=$start.ToUniversalTime().ToString("o")
    ready_at_utc=$readyAt.ToUniversalTime().ToString("o")
    runtime_startup_seconds=[math]::Round(($readyAt-$start).TotalSeconds,3)
    image_pull_excluded=$true
    functional_smoke=$functional
    cpu_percent=$stats.CPUPerc
    memory_usage=$stats.MemUsage
    memory_percent=$stats.MemPerc
    network_io=$stats.NetIO
    block_io=$stats.BlockIO
    passed=($ready -and $functional)
  }

  $result | ConvertTo-Json -Depth 10 | Set-Content -Path $out -Encoding UTF8
  $result | ConvertTo-Json -Depth 10
  Write-Host "Evidence: $out"
  if(-not $result.passed){ exit 1 }
}
catch {
  $diag = if($started){ Get-ContainerDiagnostics -Container $container }else{$null}
  $failed=[ordered]@{
    qualification="BRAIN_STORAGE_BENCH_P0B_RUNTIME_SMOKE"
    candidate=$Candidate
    image=$image
    status="HARNESS_OR_RUNTIME_FAIL"
    reason=$_.Exception.Message
    completed_at_utc=(Get-Date).ToUniversalTime().ToString("o")
    container_state=if($diag){$diag.container_state}else{$null}
    container_exit_code=if($diag){$diag.container_exit_code}else{$null}
    oom_killed=if($diag){$diag.oom_killed}else{$null}
    logs_tail=if($diag){$diag.logs_tail}else{$null}
    passed=$false
  }
  $failed | ConvertTo-Json -Depth 10 | Set-Content -Path $out -Encoding UTF8
  $failed | ConvertTo-Json -Depth 10
  Write-Host "Evidence: $out"
  exit 1
}
finally {
  if($started -and $dockerReady){
    try {
      Invoke-NativeExit -FilePath "docker" -Arguments @(
        "compose","-f",$compose,"--profile",$Candidate,
        "down","-v","--remove-orphans"
      ) | Out-Null
    } catch {}
  }
}
