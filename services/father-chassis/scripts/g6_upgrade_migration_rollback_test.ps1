$ErrorActionPreference = "Stop"

$canonicalImage = "father-chassis-father-chassis:latest"
$rollbackImage = "father-chassis:g6.4-rollback-a"
$volume = "father_g6_4_upgrade_data"
$candidateName = "father-g6-4-candidate"
$rollbackName = "father-g6-4-rollback"
$badName = "father-g6-4-bad-upgrade"
$port = 18084
$base = "http://localhost:$port"
$artifactDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\artifacts"))
$summaryPath = Join-Path $artifactDir "g6_4_upgrade_migration_rollback_summary.json"
$seedScriptPath = Join-Path $artifactDir "g6_4_seed_legacy.py"
$checkScriptPath = Join-Path $artifactDir "g6_4_check_migration.py"
$integrityScriptPath = Join-Path $artifactDir "g6_4_check_integrity.py"
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null

function Remove-ContainerIfExists([string]$name) {
    $saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        docker rm -f $name *> $null
    } finally {
        $ErrorActionPreference = $saved
    }
}

function Wait-Ready([string]$containerName) {
    $deadline = (Get-Date).AddMinutes(2)
    do {
        try {
            $r = Invoke-RestMethod "$base/health/ready" -TimeoutSec 3
            if ($r.ready) { return }
        } catch {}
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)
    docker logs --tail=120 $containerName
    throw "$containerName did not become ready"
}

Write-Host "[G6.4 1/9] Validate canonical image and prepare rollback image A"
docker image inspect $canonicalImage | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Canonical image is missing" }
docker tag $canonicalImage $rollbackImage
if ($LASTEXITCODE -ne 0) { throw "Could not tag rollback image A" }

Write-Host "[G6.4 2/9] Create isolated qualification volume"
Remove-ContainerIfExists $candidateName
Remove-ContainerIfExists $rollbackName
Remove-Item $seedScriptPath,$checkScriptPath,$integrityScriptPath -Force -ErrorAction SilentlyContinue
Remove-ContainerIfExists $badName
$existingVolume = docker volume ls -q --filter "name=^$volume$"
if ($existingVolume) { docker volume rm $volume | Out-Null }
docker volume create $volume | Out-Null

Write-Host "[G6.4 3/9] Seed legacy knowledge schema and persistent evidence"
$legacyPython = @'
import sqlite3
from pathlib import Path

root = Path("/app/data")
root.mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(root / "knowledge.db")
db.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, source TEXT NOT NULL, text TEXT NOT NULL)")
db.execute(
    "INSERT INTO chunks(source,text) VALUES(?,?)",
    ("g6.4-legacy", "G6.4 legacy evidence survives schema migration and rollback."),
)
db.commit()
db.close()
'@
Set-Content -Path $seedScriptPath -Value $legacyPython -Encoding UTF8
docker run --rm --user 0 -v "$volume`:/app/data" -v "$artifactDir`:/qualification" $rollbackImage python /qualification/g6_4_seed_legacy.py
if ($LASTEXITCODE -ne 0) { throw "Could not seed legacy datastore" }

Write-Host "[G6.4 4/9] Start candidate B against legacy datastore and trigger migration"
docker run -d --name $candidateName -p "$port`:8080" -e FATHER_DATA_DIR=/app/data -v "$volume`:/app/data" -v "$artifactDir`:/qualification" $canonicalImage uvicorn father.api_modular:app --host 0.0.0.0 --port 8080 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Candidate B could not start" }
Wait-Ready $candidateName

Write-Host "[G6.4 5/9] Verify schema migration and legacy data preservation"
$migrationPython = @'
import sqlite3

db = sqlite3.connect("/app/data/knowledge.db")
cols = [row[1] for row in db.execute("PRAGMA table_info(chunks)")]
row = db.execute(
    "SELECT source,text,content_hash FROM chunks WHERE source=?",
    ("g6.4-legacy",),
).fetchone()
print("content_hash" in cols, bool(row and row[2]), row[0] if row else "")
'@
Set-Content -Path $checkScriptPath -Value $migrationPython -Encoding UTF8
$migrationCheck = docker exec $candidateName python /qualification/g6_4_check_migration.py
if ($LASTEXITCODE -ne 0) { throw "Migration inspection failed" }
if (($migrationCheck -join " ") -notmatch "True True g6.4-legacy") { throw "Legacy schema/data migration was not proven: $migrationCheck" }

$runBody = @{ input = "What does the G6.4 legacy evidence prove?" } | ConvertTo-Json
$run = Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $runBody -TimeoutSec 60
if ([string]::IsNullOrWhiteSpace($run.trace_id)) { throw "Post-migration runtime trace missing" }
if (@($run.evidence).Count -lt 1) { throw "Post-migration runtime did not retrieve evidence" }
$preRollbackTrace = $run.trace_id

Write-Host "[G6.4 6/9] Stop candidate B and execute intentionally failed upgrade"
docker rm -f $candidateName | Out-Null
$savedPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = "Continue"
    docker run --name $badName -p "$port`:8080" -v "$volume`:/app/data" $canonicalImage sh -c "echo intentional-g6.4-upgrade-failure >&2; exit 42" | Out-Host
    $badStart = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $savedPreference
}
if ($badStart -eq 0) { throw "Failed-upgrade simulation unexpectedly succeeded" }
Remove-ContainerIfExists $badName

Write-Host "[G6.4 7/9] Roll back to image A using the same migrated datastore"
docker run -d --name $rollbackName -p "$port`:8080" -e FATHER_DATA_DIR=/app/data -v "$volume`:/app/data" -v "$artifactDir`:/qualification" $rollbackImage uvicorn father.api_modular:app --host 0.0.0.0 --port 8080 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Rollback image A could not start" }
Wait-Ready $rollbackName

Write-Host "[G6.4 8/9] Prove data integrity and runtime function after rollback"
$postBody = @{ input = "What does the G6.4 legacy evidence prove?" } | ConvertTo-Json
$post = Invoke-RestMethod "$base/run" -Method Post -ContentType "application/json" -Body $postBody -TimeoutSec 60
if ([string]::IsNullOrWhiteSpace($post.trace_id)) { throw "Post-rollback trace missing" }
if (@($post.evidence).Count -lt 1) { throw "Legacy evidence missing after rollback" }
$audit = Invoke-RestMethod "$base/audit/$($post.trace_id)"
if (@($audit.events).Count -lt 2) { throw "Post-rollback audit trail incomplete" }
$integrityPython = @'
import sqlite3

db = sqlite3.connect("/app/data/knowledge.db")
row = db.execute(
    "SELECT source,text,content_hash FROM chunks WHERE source=?",
    ("g6.4-legacy",),
).fetchone()
print(bool(row), bool(row and row[2]))
'@
Set-Content -Path $integrityScriptPath -Value $integrityPython -Encoding UTF8
$integrity = docker exec $rollbackName python /qualification/g6_4_check_integrity.py
if ($LASTEXITCODE -ne 0) { throw "Persistent datastore integrity inspection failed" }
if (($integrity -join " ") -notmatch "True True") { throw "Persistent datastore integrity failed after rollback" }

Write-Host "[G6.4 9/9] Produce qualification evidence"
$result = [ordered]@{
    qualification = "G6.4_UPGRADE_MIGRATION_ROLLBACK"
    passed = $true
    rollback_image = $rollbackImage
    candidate_image = $canonicalImage
    qualification_volume = $volume
    legacy_schema_migrated = $true
    legacy_data_preserved_after_upgrade = $true
    intentional_upgrade_failure_observed = $true
    rollback_ready = $true
    legacy_data_preserved_after_rollback = $true
    post_migration_trace_id = $preRollbackTrace
    post_rollback_trace_id = $post.trace_id
    post_rollback_evidence_count = @($post.evidence).Count
    post_rollback_audit_event_count = @($audit.events).Count
}
$result | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $summaryPath
Write-Host ""
Write-Host "G6.4 UPGRADE + MIGRATION + ROLLBACK QUALIFICATION: PASS"
$result | ConvertTo-Json -Depth 10
Remove-ContainerIfExists $rollbackName