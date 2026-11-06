import pytest

from father_fua.compatibility import CompatibilityMatrix


def test_compatibility_pass_fail_unknown_and_evidence():
    matrix=CompatibilityMatrix()
    assert matrix.status("model","prompt","skill","runtime")=="UNKNOWN"
    assert matrix.is_approved("model","prompt","skill","runtime") is False

    matrix.approve("model","prompt","skill","runtime",evidence_id="E-COMP-1")
    assert matrix.status("model","prompt","skill","runtime")=="PASS"
    assert matrix.is_approved("model","prompt","skill","runtime") is True
    assert matrix.evidence_id("model","prompt","skill","runtime")=="E-COMP-1"

    matrix.reject("model","prompt","skill","runtime",evidence_id="E-COMP-2",reason="regression")
    assert matrix.status("model","prompt","skill","runtime")=="FAIL"
    assert matrix.is_approved("model","prompt","skill","runtime") is False
    assert matrix.evidence_id("model","prompt","skill","runtime")=="E-COMP-2"


def test_compatibility_rejects_invalid_status_and_empty_parts():
    matrix=CompatibilityMatrix()
    with pytest.raises(ValueError):
        matrix.record("model",status="MAYBE")
    with pytest.raises(ValueError):
        matrix.record("",status="PASS")
