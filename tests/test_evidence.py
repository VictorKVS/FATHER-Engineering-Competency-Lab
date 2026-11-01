from dataclasses import replace
from father_fua.evidence import create_evidence, verify_evidence


def test_evidence_hash_detects_tamper():
    e = create_evidence("E1","TEST",{"status":"PASS"})
    assert verify_evidence(e)
    assert not verify_evidence(replace(e,payload={"status":"FAIL"}))
