from __future__ import annotations

from father_fua.evidence import verify_evidence
from father_fua.full_assembly import FullFUAAssemblyRuntime


def test_performance_envelope_200_integrated_missions():
    runtime=FullFUAAssemblyRuntime()
    ids=set()
    evid=set()

    for i in range(200):
        r=runtime.run(f"performance envelope integrated mission {i:03d}")
        assert r.status=="PASS"
        assert r.audit_ok is True
        assert verify_evidence(r.evidence)
        assert r.mission_id not in ids
        assert r.evidence.evidence_id not in evid
        ids.add(r.mission_id)
        evid.add(r.evidence.evidence_id)

    assert len(ids)==200
    assert len(evid)==200
    assert runtime.audit.verify() is True
