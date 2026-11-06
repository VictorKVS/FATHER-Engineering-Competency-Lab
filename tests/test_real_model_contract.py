from dataclasses import fields

from father_fua.real_model_runtime import RealModelMissionResult


def test_real_model_mission_result_contract():
    names={f.name for f in fields(RealModelMissionResult)}
    assert names=={
        "mission_id",
        "model",
        "response",
        "response_sha256",
        "latency_ms",
        "evidence",
        "audit_ok",
    }
    assert "status" not in names
