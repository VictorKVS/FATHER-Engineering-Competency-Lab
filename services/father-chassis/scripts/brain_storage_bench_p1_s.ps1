param(
  [ValidateSet("all","rel","vec")]
  [string]$League = "all"
)
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$compose = Join-Path $serviceDir "benchmarks\brain-storage\compose.yaml"
$pythonBench = Join-Path $serviceDir "benchmarks\brain-storage\p1_s_benchmark.py"
$artifactDir = Join-Path $serviceDir "artifacts\local\brain-storage-bench\p1"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$python = (Get-Command python -ErrorAction Stop).Source
$dependencyCheck = & $python -c "import psycopg; print(psycopg.__version__)" 2>&1
if($LASTEXITCODE -ne 0){
  Write-Host "P1_ENVIRONMENT_BLOCKED: psycopg is not installed."
  Write-Host 'Install: python -m pip install "psycopg[binary]>=3.2"'
  exit 2
}

$matrix = @()
if($League -eq "all" -or $League -eq "rel"){
  $matrix += [pscustomobject]@{ League="rel"; Candidate="postgres" }
  $matrix += [pscustomobject]@{ League="rel"; Candidate="pgvector" }
}
if($League -eq "all" -or $League -eq "vec"){
  $matrix += [pscustomobject]@{ League="vec"; Candidate="pgvector" }
  $matrix += [pscustomobject]@{ League="vec"; Candidate="qdrant" }
}

$results=@()
foreach($item in $matrix){
  $candidate=$item.Candidate
  $league=$item.League
  $date=Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
  $out=Join-Path $artifactDir ("P1_" + $league.ToUpper() + "_S_" + $candidate + "_" + $date + ".json")

  Write-Host ""
  Write-Host "============================================================"
  Write-Host "[P1] $($league.ToUpper())-S : $candidate"
  Write-Host "============================================================"

  docker compose -f $compose --profile $candidate up -d --pull never $candidate
  if($LASTEXITCODE -ne 0){
    $results += [ordered]@{league=$league; candidate=$candidate; status="START_FAILED"; passed=$false}
    continue
  }

  try {
    $deadline=(Get-Date).AddSeconds(120)
    $ready=$false
    while((Get-Date) -lt $deadline -and -not $ready){
      Start-Sleep -Seconds 1
      switch($candidate){
        "postgres" {
          docker exec father-bench-postgres pg_isready -U father -d father_bench *> $null
          $ready=($LASTEXITCODE -eq 0)
        }
        "pgvector" {
          docker exec father-bench-pgvector pg_isready -U father -d father_bench *> $null
          $ready=($LASTEXITCODE -eq 0)
        }
        "qdrant" {
          try {
            Invoke-RestMethod -Uri "http://127.0.0.1:56333/" -TimeoutSec 2 | Out-Null
            $ready=$true
          } catch {}
        }
      }
    }

    if(-not $ready){
      $results += [ordered]@{league=$league; candidate=$candidate; status="READINESS_FAILED"; passed=$false}
      continue
    }

    $child=Start-Process -FilePath $python -ArgumentList @(
      $pythonBench,
      "--league",$league,
      "--candidate",$candidate,
      "--out",$out
    ) -Wait -PassThru -NoNewWindow

    $payload=$null
    if(Test-Path $out){
      $payload=Get-Content $out -Raw | ConvertFrom-Json
    }
    $passed=($child.ExitCode -eq 0 -and $null -ne $payload -and $payload.result.passed)

    $results += [ordered]@{
      league=$league
      candidate=$candidate
      evidence_path=$out
      exit_code=$child.ExitCode
      passed=[bool]$passed
    }
  }
  finally {
    docker compose -f $compose --profile $candidate down -v --remove-orphans *> $null
  }
}

$date=Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$summaryPath=Join-Path $artifactDir ("P1_S_SUMMARY_" + $date + ".json")
$summary=[ordered]@{
  qualification="BRAIN_STORAGE_BENCH_P1_S_BATCH"
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
$results | Format-Table league,candidate,passed,evidence_path -AutoSize

if(-not $summary.passed){ exit 1 }
