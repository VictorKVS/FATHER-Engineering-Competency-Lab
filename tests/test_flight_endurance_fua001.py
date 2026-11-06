from __future__ import annotations

from father_fua.evidence import verify_evidence
from father_fua.full_assembly import FullFUAAssemblyRuntime


def test_endurance_100_sequential_missions_single_runtime():
    runtime=FullFUAAssemblyRuntime()
    mission_ids=set()
    evidence_ids=set()

    for i in range(100):
        r=runtime.run(f"endurance mission {i:03d}")
        assert r.status=="PASS"
        assert r.audit_ok is True
        assert verify_evidence(r.evidence)
        assert r.mission_id not in mission_ids
        assert r.evidence.evidence_id not in evidence_ids
        mission_ids.add(r.mission_id)
        evidence_ids.add(r.evidence.evidence_id)
        assert r.answer["sandbox_network_allowed"] is False
        assert r.answer["human_release_approved"] is False
        assert r.answer["learning_proposal_approved"] is False

    assert len(mission_ids)==100
    assert len(evidence_ids)==100
    assert runtime.audit.verify() is True


def test_endurance_runtime_remains_usable_after_long_sequence():
    runtime=FullFUAAssemblyRuntime()
    for i in range(50):
        runtime.run(f"warm endurance {i:03d}")
    final=runtime.run("post endurance health mission")
    assert final.status=="PASS"
    assert final.audit_ok is True
    assert verify_evidence(final.evidence)
