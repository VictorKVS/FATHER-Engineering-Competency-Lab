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



def test_auditor_accepts_controlled_testing_phase(tmp_path):
    root=tmp_path
    manifest_path=root/"factory/chassis/FUA-001/manifest.json"
    manifest_path.parent.mkdir(parents=True)

    manifest={
        "status":"INSTALLATION_APPROVED_FOR_TESTING",
        "production_ready":False,
        "installation_permit":"PASS",
        "human_acceptance":{"status":"PASS"},
        "installation_gate":{"status":"PASS"},
        "next_factory_gates":[
            "PRODUCT_TEST",
            "PILOT_TEST",
            "PRODUCTION_READINESS_REVIEW",
        ],
        "local_evm_evidence":{"full_01_26_assembly":"PASS"},
        "restricted_trustlevel_evm":{
            "status":"BLOCKED_BY_OS_CAPABILITY",
            "counted_as_pass":False,
        },
        "full_polygon_real_runtime":{
            "side_effects":0,
            "scenario_count":3,
            "pass_count":3,
        },
        "ci_evidence":{
            "component_and_assembly_tests":"PASS",
            "full_01_26_assembly":"PASS",
            "live_http_full_assembly_endpoint":"PASS",
            "sast_bandit":"PASS",
            "sca_pip_audit":"PASS",
            "secret_scan":"PASS",
            "cyclonedx_sbom":"PASS",
        },
    }
    for key in (
        "real_model_preflight",
        "real_model_mission",
        "real_model_benchmark",
        "real_model_polygon",
        "process_sandbox_evm",
        "network_isolation_evm",
        "filesystem_acl_evm",
        "full_polygon_real_runtime",
        "reliability_gate_evm",
        "sandbox_stress_evm",
        "fault_recovery_stress_evm",
    ):
        manifest.setdefault(key,{})["status"]="PASS"

    manifest_path.write_text(json.dumps(manifest),encoding="utf-8")

    from father_fua.evidence_auditor import REQUIRED_EVIDENCE, REQUIRED_RUNTIME_FILES, REQUIRED_TEST_FILES
    for rel in (*REQUIRED_EVIDENCE,*REQUIRED_RUNTIME_FILES,*REQUIRED_TEST_FILES):
        p=root/rel
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("stub",encoding="utf-8")

    findings=audit_repository(root)
    assert findings==[]


def test_auditor_rejects_testing_phase_without_permit(tmp_path):
    root=tmp_path
    manifest_path=root/"factory/chassis/FUA-001/manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest={
        "status":"INSTALLATION_APPROVED_FOR_TESTING",
        "production_ready":False,
        "installation_permit":"DENIED",
        "human_acceptance":{"status":"PASS"},
        "installation_gate":{"status":"PASS"},
        "next_factory_gates":[
            "PRODUCT_TEST",
            "PILOT_TEST",
            "PRODUCTION_READINESS_REVIEW",
        ],
    }
    manifest_path.write_text(json.dumps(manifest),encoding="utf-8")
    findings=audit_repository(root)
    assert any(f.code=="TESTING_PHASE_WITHOUT_INSTALLATION_PERMIT" for f in findings)
