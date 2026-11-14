param(
  [ValidateSet("M","L","XL")]
  [string]$Profile = "M",
  [ValidateSet("all","rel","vec")]
  [string]$League = "all"
)
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir=Split-Path -Parent $PSScriptRoot
$compose=Join-Path $serviceDir "benchmarks\brain-storage\compose.scale.yaml"
$bench=Join-Path $serviceDir "benchmarks\brain-storage\p1_scale_benchmark.py"
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

$records=@{M=100000;L=1000000;XL=10000000}[$Profile]
Write-Host "FATHER P1 SCALE PROFILE $Profile : $records records"

if($Profile -eq "XL"){
  $dockerInfo=Invoke-NativeCapture "docker" @("info","--format","{{.MemTotal}}")
  if($dockerInfo.ExitCode -eq 0){
    $dockerMem=[double]$dockerInfo.Output
    $rawVectorBytes=[double]$records * 384 * 4
    Write-Host ("Raw float32 vector payload estimate: {0:N2} GiB" -f ($rawVectorBytes/1GB))
    Write-Host ("Docker memory visible: {0:N2} GiB" -f ($dockerMem/1GB))
    Write-Host "XL will continue, but resource exhaustion must be recorded as an envelope limit, not hidden."
  }
}

$matrix=@()
if($League -eq "all" -or $League -eq "rel"){
  $matrix += [pscustomobject]@{League="rel";Candidate="postgres"}
  $matrix += [pscustomobject]@{League="rel";Candidate="pgvector"}
}
if($League -eq "all" -or $League -eq "vec"){
  $matrix += [pscustomobject]@{League="vec";Candidate="pgvector"}
  $matrix += [pscustomobject]@{League="vec";Candidate="qdrant"}
}

$results=@()
foreach($item in $matrix){
  $league=$item.League
  $candidate=$item.Candidate
  $date=Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
  $out=Join-Path $artifactDir ("P1_" + $Profile + "_" + $league.ToUpper() + "_" + $candidate + "_" + $date + ".json")

  Write-Host ""
  Write-Host "============================================================"
  Write-Host "[P1-$Profile] $($league.ToUpper()) : $candidate"
  Write-Host "============================================================"

  $up=Invoke-NativeCapture "docker" @(
    "compose","-f",$compose,"--profile",$candidate,"up","-d","--pull","never",$candidate
  )
  if($up.ExitCode -ne 0){
    $results += [ordered]@{league=$league;candidate=$candidate;status="START_FAILED";passed=$false;reason=$up.Output}
    continue
  }

  try {
    $deadline=(Get-Date).AddSeconds(180)
    $ready=$false
    while((Get-Date) -lt $deadline -and -not $ready){
      Start-Sleep -Seconds 1
      if($candidate -eq "postgres"){
        $probe=Invoke-NativeCapture "docker" @("exec","father-bench-postgres","pg_isready","-U","father","-d","father_bench")
        $ready=($probe.ExitCode -eq 0)
      } elseif($candidate -eq "pgvector"){
        $probe=Invoke-NativeCapture "docker" @("exec","father-bench-pgvector","pg_isready","-U","father","-d","father_bench")
        $ready=($probe.ExitCode -eq 0)
      } else {
        try {
          Invoke-RestMethod -Uri "http://127.0.0.1:56333/" -TimeoutSec 2 | Out-Null
          $ready=$true
        } catch {}
      }
    }

    if(-not $ready){
      $results += [ordered]@{league=$league;candidate=$candidate;status="READINESS_FAILED";passed=$false}
      continue
    }

    $child=Start-Process -FilePath $python -ArgumentList @(
      $bench,
      "--profile",$Profile,
      "--league",$league,
      "--candidate",$candidate,
      "--out",$out
    ) -Wait -PassThru -NoNewWindow

    $payload=$null
    if(Test-Path $out){$payload=Get-Content $out -Raw | ConvertFrom-Json}
    $passed=$false
    if($null -ne $payload -and $null -ne $payload.PSObject.Properties["result"]){
      $passed=[bool]$payload.result.passed
    }

    $results += [ordered]@{
      league=$league
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
$summaryPath=Join-Path $artifactDir ("P1_" + $Profile + "_SUMMARY_" + $date + ".json")
$summary=[ordered]@{
  qualification="BRAIN_STORAGE_BENCH_P1_SCALE_BATCH"
  profile=$Profile
  records=$records
  timestamp_utc=(Get-Date).ToUniversalTime().ToString("o")
  results=$results
  pass_count=@($results | Where-Object {$_.passed}).Count
  fail_count=@($results | Where-Object {-not $_.passed}).Count
  passed=(@($results | Where-Object {-not $_.passed}).Count -eq 0)
}
$summary | ConvertTo-Json -Depth 10 | Set-Content $summaryPath -Encoding UTF8
$summary | ConvertTo-Json -Depth 10
Write-Host "Summary evidence: $summaryPath"
$results | Format-Table league,candidate,passed,evidence_path -AutoSize
if(-not $summary.passed){exit 1}
