from dataclasses import replace
from father_fua.audit import AuditLog


def test_audit_chain_verifies():
    a = AuditLog()
    a.append(kind="mission", actor="user", correlation_id="C1", detail={"x":1})
    a.append(kind="policy", actor="engine", correlation_id="C1", detail={"decision":"ALLOW"})
    assert a.verify() is True


def test_tamper_breaks_chain():
    a = AuditLog()
    a.append(kind="mission", actor="user", correlation_id="C1", detail={"x":1})
    a.events[0] = replace(a.events[0], detail={"x":2})
    assert a.verify() is False



def test_timestamp_tamper_breaks_chain():
    a = AuditLog()
    a.append(kind="mission", actor="user", correlation_id="C1", detail={"x":1})
    a.events[0] = replace(a.events[0], ts=a.events[0].ts + 1)
    assert a.verify() is False
