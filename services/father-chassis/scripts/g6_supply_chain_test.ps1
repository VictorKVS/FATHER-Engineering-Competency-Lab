$ErrorActionPreference="Stop"
$fail=@()
Write-Host "[G6.4] Dependency integrity / inventory"

$images=@("python:3.12-slim","pgvector/pgvector:pg16","redis:7-alpine")
$inventory=@()
foreach($img in $images){
    docker image inspect $img *> $null
    if($LASTEXITCODE -ne 0){$fail += "missing_image:$img";continue}
    $id=docker image inspect $img --format '{{.Id}}'
    $digests=docker image inspect $img --format '{{json .RepoDigests}}'
    $inventory += [ordered]@{image=$img;id=$id;repo_digests=$digests}
}
$gitStatus=(git status --porcelain)
if($LASTEXITCODE -ne 0){$fail+="git_status_failed"}

$result=[ordered]@{
 gate="G6.4_SUPPLY_CHAIN"
 images=$inventory
 working_tree_clean=[string]::IsNullOrWhiteSpace(($gitStatus -join ""))
 failures=$fail
 passed=($fail.Count -eq 0)
}
$result|ConvertTo-Json -Depth 10|Set-Content ".\artifacts\g6_supply_chain.json"
$result|ConvertTo-Json -Depth 10
if(-not $result.passed){Write-Host "G6.4 SUPPLY CHAIN: FAIL";exit 1}
Write-Host "G6.4 SUPPLY CHAIN: PASS"
