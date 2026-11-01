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



def test_blocked_restricted_gate_cannot_be_counted_as_pass(tmp_path):
    root=Path(".")
    shutil.copytree(root/"factory", tmp_path/"factory")
    shutil.copytree(root/"father_fua", tmp_path/"father_fua")
    shutil.copytree(root/"tests", tmp_path/"tests")
    manifest_path=tmp_path/"factory/chassis/FUA-001/manifest.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["restricted_trustlevel_evm"]["status"]="BLOCKED_BY_OS_CAPABILITY"
    manifest["restricted_trustlevel_evm"]["counted_as_pass"]=True
    manifest_path.write_text(json.dumps(manifest),encoding="utf-8")
    findings=audit_repository(tmp_path)
    assert any(f.code=="BLOCKED_GATE_MISREPRESENTED_AS_PASS" for f in findings)


def test_polygon_side_effect_denies_final_evidence_gate(tmp_path):
    root=Path(".")
    shutil.copytree(root/"factory", tmp_path/"factory")
    shutil.copytree(root/"father_fua", tmp_path/"father_fua")
    shutil.copytree(root/"tests", tmp_path/"tests")
    manifest_path=tmp_path/"factory/chassis/FUA-001/manifest.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["full_polygon_real_runtime"]["side_effects"]=1
    manifest_path.write_text(json.dumps(manifest),encoding="utf-8")
    findings=audit_repository(tmp_path)
    assert any(f.code=="POLYGON_SIDE_EFFECT_DETECTED" for f in findings)
