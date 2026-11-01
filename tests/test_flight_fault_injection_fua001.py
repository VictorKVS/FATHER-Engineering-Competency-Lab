from __future__ import annotations

from father_fua.audit import AuditLog
from father_fua.evidence import create_evidence, verify_evidence
from father_fua.recovery import retry


def test_transient_fault_recovers_with_bounded_retry():
    calls={"n":0}

    def op():
        calls["n"]+=1
        if calls["n"]<3:
            raise TimeoutError("transient")
        return "RECOVERED"

    assert retry(op,attempts=3,retryable_exceptions=(TimeoutError,))=="RECOVERED"
    assert calls["n"]==3


def test_security_denial_is_not_retried():
    calls={"n":0}

    def op():
        calls["n"]+=1
        raise PermissionError("denied")

    try:
        retry(op,attempts=5)
    except PermissionError:
        pass
    else:
        raise AssertionError("PermissionError must escape")

    assert calls["n"]==1


def test_evidence_and_audit_survive_fault_sequence():
    audit=AuditLog()
    evidences=[]

    for i in range(25):
        audit.append(
            kind="fault.injected",
            actor="FUA-001",
            correlation_id=f"fault-{i}",
            detail={"index":i,"class":"synthetic"},
        )
        ev=create_evidence(
            f"EVID-FAULT-{i}",
            "FLIGHT_FAULT_INJECTION",
            {"index":i,"expected":"contained"},
        )
        assert verify_evidence(ev)
        evidences.append(ev)

    assert audit.verify() is True
    assert len({e.evidence_id for e in evidences})==25
