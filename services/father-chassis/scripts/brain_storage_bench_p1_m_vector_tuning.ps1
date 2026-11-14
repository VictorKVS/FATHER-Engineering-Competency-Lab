param(
  [ValidateSet("all","pgvector","qdrant")]
  [string]$Candidate = "all"
)
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir=Split-Path -Parent $PSScriptRoot
$compose=Join-Path $serviceDir "benchmarks\brain-storage\compose.yaml"
$bench=Join-Path $serviceDir "benchmarks\brain-storage\p1_m_vector_tuning.py"
$artifactDir=Join-Path $serviceDir "artifacts\local\brain-storage-bench\p1-scale"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null
$python=(Get-Command python -ErrorAction Stop).Source

function Invoke-NativeCapture {
  param([string]$FilePath,[string[]]$Arguments)
  $previous=$ErrorActionPreference
  try {
    $ErrorActionPreference="Continue"
    $lines=& $FilePath @Arguments 2>&1
    [pscustomobject]@{
      ExitCode=$LASTEXITCODE
      Output=($lines | Out-String).Trim()
    }
  } finally {
    $ErrorActionPreference=$previous
  }
}

$candidates=if($Candidate -eq "all"){@("pgvector","qdrant")}else{@($Candidate)}
$results=@()

foreach($candidate in $candidates){
  $date=Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
  $out=Join-Path $artifactDir ("P1_M_VEC_TUNING_" + $candidate + "_" + $date + ".json")

  Write-Host ""
  Write-Host "============================================================"
  Write-Host "[P1-M TUNING] $candidate"
  Write-Host "============================================================"

  $up=Invoke-NativeCapture "docker" @(
    "compose","-f",$compose,"--profile",$candidate,"up","-d","--pull","never",$candidate
  )
  if($up.ExitCode -ne 0){
    $results += [ordered]@{candidate=$candidate;status="START_FAILED";passed=$false;reason=$up.Output}
    continue
  }

  try {
    $deadline=(Get-Date).AddSeconds(180)
    $ready=$false
    while((Get-Date) -lt $deadline -and -not $ready){
      Start-Sleep -Seconds 1
      if($candidate -eq "pgvector"){
        $probe=Invoke-NativeCapture "docker" @(
          "exec","father-bench-pgvector","pg_isready","-U","father","-d","father_bench"
        )
        $ready=($probe.ExitCode -eq 0)
      } else {
        try {
          Invoke-RestMethod -Uri "http://127.0.0.1:56333/" -TimeoutSec 2 | Out-Null
          $ready=$true
        } catch {}
      }
    }

    if(-not $ready){
      $results += [ordered]@{candidate=$candidate;status="READINESS_FAILED";passed=$false}
      continue
    }

    $child=Start-Process -FilePath $python -ArgumentList @(
      $bench,"--candidate",$candidate,"--out",$out
    ) -Wait -PassThru -NoNewWindow

    $payload=$null
    if(Test-Path $out){$payload=Get-Content $out -Raw | ConvertFrom-Json}
    $passed=$false
    if($null -ne $payload -and $null -ne $payload.PSObject.Properties["result"]){
      $passed=[bool]$payload.result.passed
    }

    $results += [ordered]@{
      candidate=$candidate
      evidence_path=$out
      exit_code=$child.ExitCode
      passed=$passed
    }
  }
  finally {
    $down=Invoke-NativeCapture "docker" @(
      "compose","-f",$compose,"--profile",$candidate,"down","-v","--remove-orphans"
    )
    if($down.ExitCode -ne 0){Write-Warning "Cleanup failed for $candidate"}
  }
}

$date=Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$summaryPath=Join-Path $artifactDir ("P1_M_VEC_TUNING_SUMMARY_" + $date + ".json")
$summary=[ordered]@{
  qualification="BRAIN_STORAGE_BENCH_P1_M_VECTOR_TUNING_BATCH"
  timestamp_utc=(Get-Date).ToUniversalTime().ToString("o")
  results=$results
  pass_count=@($results | Where-Object {$_.passed}).Count
  fail_count=@($results | Where-Object {-not $_.passed}).Count
  passed=(@($results | Where-Object {-not $_.passed}).Count -eq 0)
}
$summary | ConvertTo-Json -Depth 10 | Set-Content $summaryPath -Encoding UTF8
$summary | ConvertTo-Json -Depth 10
Write-Host "Summary evidence: $summaryPath"
$results | Format-Table candidate,passed,evidence_path -AutoSize
if(-not $summary.passed){exit 1}
