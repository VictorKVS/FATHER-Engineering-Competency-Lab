from pathlib import Path
import json
import shutil

from father_fua.evidence_auditor import audit_repository, repository_gate


def test_current_repository_evidence_gate_passes():
    assert repository_gate(Path("."))=="PASS"


def test_missing_evidence_denies(tmp_path):
    src=Path("factory/chassis/FUA-001/manifest.json")
    dest=tmp_path/"factory/chassis/FUA-001"
    dest.mkdir(parents=True)
    shutil.copy2(src,dest/"manifest.json")
    findings=audit_repository(tmp_path)
    assert any(f.code=="EVIDENCE_MISSING" for f in findings)
    assert repository_gate(tmp_path)=="DENY"


def test_premature_production_ready_is_critical(tmp_path):
    src=Path("factory/chassis/FUA-001/manifest.json")
    dest=tmp_path/"factory/chassis/FUA-001"
    dest.mkdir(parents=True)
    manifest=json.loads(src.read_text(encoding="utf-8"))
    manifest["production_ready"]=True
    (dest/"manifest.json").write_text(json.dumps(manifest),encoding="utf-8")
    findings=audit_repository(tmp_path)
    assert any(f.code=="PREMATURE_PRODUCTION_READY" and f.severity=="CRITICAL" for f in findings)
