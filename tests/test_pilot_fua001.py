from __future__ import annotations

from father_fua.full_assembly import FullFUAAssemblyRuntime
from father_fua.evidence import verify_evidence


def test_pilot_multiple_missions_same_runtime():
    runtime=FullFUAAssemblyRuntime()
    missions=[
        "summarize internal architecture state",
        "check policy and tool boundary",
        "produce controlled testing evidence summary",
        "evaluate compatibility state",
        "verify recovery readiness",
    ]

    results=[runtime.run(m) for m in missions]

    assert all(r.status=="PASS" for r in results)
    assert all(r.audit_ok is True for r in results)
    assert all(verify_evidence(r.evidence) for r in results)
    assert all(r.readiness=="DENIED" for r in results)
    assert runtime.audit.verify() is True
    assert runtime.metrics.counters.get(("missions_completed",(("agent","FUA-001"),)),0)==5


def test_pilot_unique_mission_and_evidence_ids():
    runtime=FullFUAAssemblyRuntime()
    results=[runtime.run(f"pilot mission {i}") for i in range(5)]
    mission_ids={r.mission_id for r in results}
    evidence_ids={r.evidence.evidence_id for r in results}
    assert len(mission_ids)==5
    assert len(evidence_ids)==5


def test_pilot_no_self_approval_or_network_enablement():
    runtime=FullFUAAssemblyRuntime()
    result=runtime.run("pilot safety invariant")
    assert result.answer["human_release_approved"] is False
    assert result.answer["learning_proposal_approved"] is False
    assert result.answer["sandbox_network_allowed"] is False
