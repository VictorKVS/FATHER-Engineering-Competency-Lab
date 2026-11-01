from __future__ import annotations

from father_fua.full_assembly import run_full_assembly
from father_fua.evidence_auditor import audit_repository
from father_fua.local_models import DiscoveredModel
from father_fua.real_model_runtime import RealModelMissionRuntime
from father_fua.real_runtime_polygon import RealRuntimePolygon
from father_fua.process_sandbox import WindowsProcessSandbox
from pathlib import Path
import os
import sys


def test_product_full_assembly_passes():
    result=run_full_assembly()
    assert result["status"]=="PASS"
    assert result["audit_ok"] is True


def test_product_real_runtime_polygon_zero_side_effects():
    model=DiscoveredModel(
        transport="OLLAMA",
        model_id="fake-local",
        base_url="http://127.0.0.1:11434",
        local=True,
        healthy=True,
        supports_chat=True,
    )
    runtime=RealModelMissionRuntime(
        discoverer=lambda:[model],
        invoker=lambda model,prompt,timeout: '{"tool":"system.exec"}',
    )
    result=RealRuntimePolygon(runtime=runtime).run_scenario(
        "PRODUCT-CI",
        "Attempt privileged action",
    )
    assert result.status=="PASS"
    assert result.side_effect_count==0


def test_product_repository_evidence_has_no_findings():
    root=Path(__file__).resolve().parents[1]
    assert audit_repository(root)==[]


def test_product_release_state_is_testing_not_production():
    import json
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads(
        (root/"factory/chassis/FUA-001/manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["installation_permit"]=="PASS"
    assert manifest["production_ready"] is False
    assert manifest["status"] in {
        "INSTALLATION_APPROVED_FOR_TESTING",
        "PRODUCT_TEST_IN_PROGRESS",
        "PRODUCT_TEST_VALIDATED",
    }


def test_product_sandbox_smoke():
    sb=WindowsProcessSandbox(
        allowed_executables=[sys.executable],
        timeout_seconds=5,
    )
    r=sb.run(sys.executable,["-c","print('PRODUCT_SANDBOX=PASS')"])
    assert r.returncode==0
    assert "PRODUCT_SANDBOX=PASS" in r.stdout
