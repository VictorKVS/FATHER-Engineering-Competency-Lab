from dataclasses import replace
from father_fua.evidence import create_evidence, verify_evidence


def test_evidence_hash_detects_tamper():
    e = create_evidence("E1","TEST",{"status":"PASS"})
    assert verify_evidence(e)
    assert not verify_evidence(replace(e,payload={"status":"FAIL"}))



def test_evidence_hash_binds_metadata_envelope():
    e = create_evidence(
        "E2",
        "TEST",
        {"status":"PASS"},
        provenance="polygon",
        correlation_id="C1",
        created_at=123.0,
    )
    assert verify_evidence(e)
    assert not verify_evidence(replace(e, evidence_id="E3"))
    assert not verify_evidence(replace(e, kind="OTHER"))
    assert not verify_evidence(replace(e, provenance="other"))
    assert not verify_evidence(replace(e, correlation_id="C2"))
    assert not verify_evidence(replace(e, created_at=124.0))
