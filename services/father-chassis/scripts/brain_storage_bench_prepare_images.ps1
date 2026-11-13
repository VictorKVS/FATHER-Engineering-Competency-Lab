param(
  [ValidateSet("all","postgres","pgvector","qdrant","neo4j","opensearch")]
  [string]$Candidate = "all",
  [int]$Retries = 3
)
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local\brain-storage-bench"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null
$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$out = Join-Path $artifactDir ("P0A_image_acquisition_" + $Candidate + "_" + $date + ".json")

function Invoke-NativeCapture {
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

$images=[ordered]@{
  postgres="postgres:18-alpine"
  pgvector="pgvector/pgvector:0.8.7-pg18-trixie"
  qdrant="qdrant/qdrant:latest"
  neo4j="neo4j:2026.10.2"
  opensearch="opensearchproject/opensearch:3.9.0"
}

$selected = if($Candidate -eq "all"){ @($images.Keys) } else { @($Candidate) }
$results=@()

foreach($name in $selected){
  $image=$images[$name]

  $inspectResult = Invoke-NativeCapture -FilePath "docker" -Arguments @("image","inspect",$image)
  if($inspectResult.ExitCode -eq 0){
    $inspect = $inspectResult.Output | ConvertFrom-Json
    $results += [ordered]@{
      candidate=$name
      image=$image
      status="READY_LOCAL"
      attempts=0
      image_id=$inspect[0].Id
      pulled=$false
      passed=$true
    }
    continue
  }

  $attempt=0
  $ok=$false
  $lastError=""
  $started=Get-Date

  while($attempt -lt $Retries -and -not $ok){
    $attempt++
    Write-Host "[P0A] Pull $name ($image) attempt $attempt/$Retries"

    $pullResult = Invoke-NativeCapture -FilePath "docker" -Arguments @("pull",$image)
    if($pullResult.ExitCode -eq 0){
      $ok=$true
      break
    }

    $lastError=$pullResult.Output
    if($attempt -lt $Retries){
      Start-Sleep -Seconds (5 * $attempt)
    }
  }

  if($ok){
    $inspectResult = Invoke-NativeCapture -FilePath "docker" -Arguments @("image","inspect",$image)
    if($inspectResult.ExitCode -ne 0){
      throw "Image pull reported success but inspect failed for $image"
    }
    $inspect = $inspectResult.Output | ConvertFrom-Json

    $results += [ordered]@{
      candidate=$name
      image=$image
      status="PULLED"
      attempts=$attempt
      acquisition_seconds=[math]::Round(((Get-Date)-$started).TotalSeconds,3)
      image_id=$inspect[0].Id
      pulled=$true
      passed=$true
    }
  }
  else {
    $networkBlocked = (
      $lastError -match "TLS handshake timeout" -or
      $lastError -match "timeout awaiting response headers" -or
      $lastError -match "failed to fetch anonymous token" -or
      $lastError -match "i/o timeout" -or
      $lastError -match "connection reset" -or
      $lastError -match "context deadline exceeded"
    )

    $results += [ordered]@{
      candidate=$name
      image=$image
      status=if($networkBlocked){"ENVIRONMENT_NETWORK_BLOCKED"}else{"PULL_FAILED"}
      attempts=$attempt
      acquisition_seconds=[math]::Round(((Get-Date)-$started).TotalSeconds,3)
      reason=$lastError
      pulled=$false
      passed=$false
    }
  }
}

$payload=[ordered]@{
  qualification="BRAIN_STORAGE_BENCH_P0A_IMAGE_ACQUISITION"
  timestamp_utc=(Get-Date).ToUniversalTime().ToString("o")
  candidate=$Candidate
  retries=$Retries
  results=$results
  ready_count=@($results | Where-Object {$_.passed}).Count
  blocked_count=@($results | Where-Object {-not $_.passed}).Count
  passed=(@($results | Where-Object {-not $_.passed}).Count -eq 0)
}

$payload | ConvertTo-Json -Depth 10 | Set-Content -Path $out -Encoding UTF8
$payload | ConvertTo-Json -Depth 10
Write-Host "Evidence: $out"

if(-not $payload.passed){ exit 2 }
