param()
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir=Split-Path -Parent $PSScriptRoot
$compose=Join-Path $serviceDir "benchmarks\brain-storage\compose.yaml"
$bench=Join-Path $serviceDir "benchmarks\brain-storage\p1_m_pgvector_build_tuning.py"
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

$date=Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$out=Join-Path $artifactDir ("P1_M_PGVECTOR_BUILD_TUNING_" + $date + ".json")

$up=Invoke-NativeCapture "docker" @(
  "compose","-f",$compose,"--profile","pgvector","up","-d","--pull","never","pgvector"
)
if($up.ExitCode -ne 0){
  Write-Host $up.Output
  exit 2
}

try {
  $deadline=(Get-Date).AddSeconds(180)
  $ready=$false
  while((Get-Date) -lt $deadline -and -not $ready){
    Start-Sleep -Seconds 1
    $probe=Invoke-NativeCapture "docker" @(
      "exec","father-bench-pgvector","pg_isready","-U","father","-d","father_bench"
    )
    $ready=($probe.ExitCode -eq 0)
  }
  if(-not $ready){throw "pgvector readiness timeout"}

  $child=Start-Process -FilePath $python -ArgumentList @(
    $bench,"--out",$out
  ) -Wait -PassThru -NoNewWindow

  Write-Host "Evidence: $out"
  exit $child.ExitCode
}
finally {
  $down=Invoke-NativeCapture "docker" @(
    "compose","-f",$compose,"--profile","pgvector","down","-v","--remove-orphans"
  )
  if($down.ExitCode -ne 0){Write-Warning "Cleanup failed"}
}
