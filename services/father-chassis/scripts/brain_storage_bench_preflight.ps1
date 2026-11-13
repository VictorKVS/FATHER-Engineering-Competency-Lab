param()
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local\brain-storage-bench"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null
$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$out = Join-Path $artifactDir "P0_preflight_$date.json"

$dockerReady=$false
$dockerVersion=$null
try {
  $dockerVersion = (docker version --format '{{.Server.Version}}' 2>$null)
  if($LASTEXITCODE -eq 0 -and $dockerVersion){ $dockerReady=$true }
} catch {}

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$os = Get-CimInstance Win32_OperatingSystem
$disks = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
  [ordered]@{
    device=$_.DeviceID
    size_gb=[math]::Round($_.Size/1GB,2)
    free_gb=[math]::Round($_.FreeSpace/1GB,2)
  }
}

$result=[ordered]@{
 qualification="BRAIN_STORAGE_BENCH_P0_PREFLIGHT"
 timestamp_utc=(Get-Date).ToUniversalTime().ToString("o")
 computer_name=$env:COMPUTERNAME
 os_caption=$os.Caption
 os_version=$os.Version
 cpu_name=$cpu.Name
 cpu_cores=$cpu.NumberOfCores
 cpu_logical=$cpu.NumberOfLogicalProcessors
 ram_gb=[math]::Round($os.TotalVisibleMemorySize/1MB,2)
 docker_ready=$dockerReady
 docker_server_version=$dockerVersion
 python_version=(python --version 2>&1 | Out-String).Trim()
 disks=$disks
 passed=$dockerReady
}
$result | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
$result | ConvertTo-Json -Depth 8
Write-Host "Evidence: $out"
if(-not $dockerReady){ exit 1 }
