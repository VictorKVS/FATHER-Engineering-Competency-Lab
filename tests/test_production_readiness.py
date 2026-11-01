import json
from pathlib import Path

from father_fua.production_readiness import production_readiness_decision, review_production_readiness


def test_current_repository_production_readiness_passes_with_docker_profile():
    findings=review_production_readiness(Path("."))
    assert findings==[]
    assert production_readiness_decision(Path("."))=="PASS"


def test_without_docker_profile_readiness_is_blocked(tmp_path):
    root=tmp_path
    src=Path("factory/chassis/FUA-001/manifest.json")
    dest=root/"factory/chassis/FUA-001"
    dest.mkdir(parents=True)
    manifest=json.loads(src.read_text(encoding="utf-8"))
    manifest["docker_native_containment_evm"]={"status":"NOT_RUN"}
    manifest["production_ready"]=False
    (dest/"manifest.json").write_text(json.dumps(manifest),encoding="utf-8")

    findings=review_production_readiness(root)
    codes={f.code for f in findings}
    assert production_readiness_decision(root)=="BLOCKED"
    assert "OS_TRUST_BOUNDARY_NOT_PROVEN" in codes
    assert "FINAL_NATIVE_CONTAINMENT_NOT_CERTIFIED" in codes
