$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw ".venv Python not found" }

$Commit = (git rev-parse HEAD).Trim()
$ManifestPath = Join-Path $Repo "factory\chassis\FUA-001\manifest.json"
$OutPath = Join-Path $Repo "factory\evidence\FUA-001-HUMAN-ACCEPTANCE-SNAPSHOT.json"

$TempPy = Join-Path $env:TEMP "fua-human-acceptance-snapshot.py"

@'
import json
import sys
from pathlib import Path

from father_fua.human_acceptance import snapshot_hash

commit=sys.argv[1]
manifest_path=Path(sys.argv[2])
out_path=Path(sys.argv[3])

manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
digest=snapshot_hash(commit_sha=commit,manifest=manifest)

payload={
    "schema":"father.human_acceptance_snapshot.v1",
    "chassis_id":"FUA-001",
    "commit_sha":commit,
    "manifest_status":manifest.get("status"),
    "installation_permit":manifest.get("installation_permit"),
    "production_ready":manifest.get("production_ready"),
    "next_factory_gates":manifest.get("next_factory_gates"),
    "snapshot_sha256":digest,
}
out_path.write_text(json.dumps(payload,indent=2),encoding="utf-8")

print("COMMIT SHA       :",commit)
print("MANIFEST STATUS  :",payload["manifest_status"])
print("INSTALL PERMIT   :",payload["installation_permit"])
print("PRODUCTION READY :",payload["production_ready"])
print("NEXT GATES       :",",".join(payload["next_factory_gates"] or []))
print("SNAPSHOT SHA256  :",digest)
print("SNAPSHOT FILE    :",str(out_path))
'@ | Set-Content -Path $TempPy -Encoding UTF8

try {
    & $Py $TempPy $Commit $ManifestPath $OutPath
    $Code=$LASTEXITCODE
}
finally {
    Remove-Item $TempPy -Force -ErrorAction SilentlyContinue
}

if ($Code -ne 0) {
    throw "human-acceptance snapshot generation failed with exit code $Code"
}
