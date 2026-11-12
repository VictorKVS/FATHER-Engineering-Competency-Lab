$ErrorActionPreference = "Stop"
$fail = @()
$container = "father-chassis-father-chassis-1"

Write-Host "[G6.3] Container user"
$user = docker exec $container id -u
if ($LASTEXITCODE -ne 0 -or $user.Trim() -eq "0") {
    $fail += "runtime_is_root"
}

Write-Host "[G6.3] no-new-privileges"
$nnp = docker inspect $container --format '{{json .HostConfig.SecurityOpt}}'
if ($nnp -notmatch "no-new-privileges") {
    $fail += "no_new_privileges_missing"
}

Write-Host "[G6.3] Resource limits"
$mem = [int64](docker inspect $container --format '{{.HostConfig.Memory}}')
$cpu = [int64](docker inspect $container --format '{{.HostConfig.NanoCpus}}')
if ($mem -le 0) {
    $fail += "memory_limit_missing"
}
if ($cpu -le 0) {
    $fail += "cpu_limit_missing"
}

Write-Host "[G6.3] Healthcheck"
$health = docker inspect $container --format '{{if .Config.Healthcheck}}configured{{else}}missing{{end}}'
if ($health.Trim() -ne "configured") {
    $fail += "healthcheck_missing"
}

Write-Host "[G6.3] Default credential check"
$envText = Get-Content ".env" -Raw

if ($envText -notmatch '(?m)^FATHER_POSTGRES_PASSWORD=.+$') {
    $fail += "postgres_password_missing"
}
elseif ($envText -match '(?m)^FATHER_POSTGRES_PASSWORD=(father|change-me-before-production)?\s*$') {
    $fail += "postgres_default_or_empty_password"
}

$result = [ordered]@{
    gate = "G6.3_SECURITY"
    runtime_uid = $user.Trim()
    no_new_privileges = ($nnp -match "no-new-privileges")
    memory_limit_bytes = $mem
    nano_cpus = $cpu
    healthcheck = $health.Trim()
    failures = $fail
    passed = ($fail.Count -eq 0)
}

$result | ConvertTo-Json -Depth 10 | Set-Content ".\artifacts\g6_security.json"
$result | ConvertTo-Json -Depth 10

if (-not $result.passed) {
    Write-Host "G6.3 SECURITY: FAIL"
    exit 1
}

Write-Host "G6.3 SECURITY: PASS"
