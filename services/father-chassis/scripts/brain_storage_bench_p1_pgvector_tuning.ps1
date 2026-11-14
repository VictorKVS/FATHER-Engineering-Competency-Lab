param()
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$compose = Join-Path $serviceDir "benchmarks\brain-storage\compose.yaml"
$pythonBench = Join-Path $serviceDir "benchmarks\brain-storage\p1_pgvector_tuning.py"
$artifactDir = Join-Path $serviceDir "artifacts\local\brain-storage-bench\p1"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null
$date=Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$out=Join-Path $artifactDir ("P1_VEC_S_pgvector_tuning_" + $date + ".json")

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

$up=Invoke-NativeCapture "docker" @(
  "compose","-f",$compose,"--profile","pgvector","up","-d","--pull","never","pgvector"
)
if($up.ExitCode -ne 0){
  Write-Host $up.Output
  exit 2
}

try {
  $deadline=(Get-Date).AddSeconds(120)
  $ready=$false
  while((Get-Date) -lt $deadline -and -not $ready){
    Start-Sleep -Seconds 1
    $probe=Invoke-NativeCapture "docker" @(
      "exec","father-bench-pgvector","pg_isready","-U","father","-d","father_bench"
    )
    $ready=($probe.ExitCode -eq 0)
  }
  if(-not $ready){ throw "pgvector readiness timeout" }

  $python=(Get-Command python -ErrorAction Stop).Source
  $child=Start-Process -FilePath $python -ArgumentList @(
    $pythonBench,"--out",$out
  ) -Wait -PassThru -NoNewWindow

  Write-Host "Evidence: $out"
  exit $child.ExitCode
}
finally {
  $down=Invoke-NativeCapture "docker" @(
    "compose","-f",$compose,"--profile","pgvector","down","-v","--remove-orphans"
  )
  if($down.ExitCode -ne 0){
    Write-Warning "Cleanup failed: $($down.Output)"
  }
}
