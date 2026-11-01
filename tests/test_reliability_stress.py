import time
from dataclasses import replace

import pytest

from father_fua.approval import Approval, ApprovalReplayGuard, action_hash
from father_fua.audit import AuditLog
from father_fua.evidence import create_evidence, verify_evidence
from father_fua.recovery import retry
from father_fua.resources import Budget


def test_stress_evidence_integrity_500_rounds():
    for i in range(500):
        e=create_evidence(
            f"E-STRESS-{i}",
            "STRESS",
            {"i":i,"status":"PASS"},
            provenance="stress",
            correlation_id=f"C-{i}",
            created_at=float(i+1),
        )
        assert verify_evidence(e)
        assert not verify_evidence(replace(e,payload={"i":i,"status":"FAIL"}))


def test_stress_audit_chain_500_events_and_mutation():
    audit=AuditLog()
    for i in range(500):
        audit.append(
            kind="stress.event",
            actor="FUA-001",
            correlation_id="STRESS",
            detail={"i":i},
        )
    assert audit.verify() is True
    audit.events[250]=replace(audit.events[250],detail={"i":"tampered"})
    assert audit.verify() is False


def test_stress_approval_single_use_200_rounds():
    guard=ApprovalReplayGuard()
    now=time.time()
    for i in range(200):
        payload={"index":i}
        a=Approval(
            action_hash("stress.action",payload),
            "approver",
            "APPROVE",
            now+60,
            requester="requester",
            approval_id=f"A-STRESS-{i}",
        )
        assert guard.consume(
            a,
            "stress.action",
            requester="requester",
            now=now,
            payload=payload,
        ) is True
        assert guard.consume(
            a,
            "stress.action",
            requester="requester",
            now=now,
            payload=payload,
        ) is False


def test_stress_budget_accounting_1000_consumptions():
    b=Budget(token_limit=1000,money_limit=100.0)
    for _ in range(1000):
        b.consume(tokens=1,money=0.01)
    assert b.tokens_used==1000
    assert round(b.money_used,6)==10.0
    with pytest.raises(RuntimeError):
        b.consume(tokens=1)


def test_stress_recovery_transient_then_success_100_rounds():
    for _ in range(100):
        state={"n":0}
        def op():
            state["n"] += 1
            if state["n"] < 3:
                raise RuntimeError("transient")
            return "ok"
        assert retry(op,attempts=3)=="ok"
        assert state["n"]==3


def test_stress_security_denial_never_retried_100_rounds():
    for _ in range(100):
        state={"n":0}
        def op():
            state["n"] += 1
            raise PermissionError("denied")
        with pytest.raises(PermissionError):
            retry(op,attempts=5)
        assert state["n"]==1
