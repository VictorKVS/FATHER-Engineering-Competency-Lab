import time

from father_fua.human_acceptance import (
    HumanAcceptance,
    HumanAcceptanceReplayGuard,
    snapshot_hash,
    verify_human_acceptance,
)


def test_human_acceptance_is_bound_to_exact_snapshot():
    manifest={"status":"READY_FOR_HUMAN","production_ready":False}
    snap=snapshot_hash(commit_sha="abc123",manifest=manifest)
    a=HumanAcceptance(
        acceptance_id="HA-1",
        snapshot_sha256=snap,
        requester="factory",
        approver="human",
        decision="ACCEPT",
        expires_at=time.time()+60,
    )
    assert verify_human_acceptance(a,current_snapshot_sha256=snap)
    changed=snapshot_hash(commit_sha="def456",manifest=manifest)
    assert not verify_human_acceptance(a,current_snapshot_sha256=changed)


def test_human_acceptance_requires_four_eyes_and_is_single_use():
    manifest={"status":"READY_FOR_HUMAN"}
    snap=snapshot_hash(commit_sha="abc123",manifest=manifest)

    self_approval=HumanAcceptance(
        acceptance_id="HA-SELF",
        snapshot_sha256=snap,
        requester="alice",
        approver="alice",
        decision="ACCEPT",
        expires_at=time.time()+60,
    )
    assert not verify_human_acceptance(self_approval,current_snapshot_sha256=snap)

    valid=HumanAcceptance(
        acceptance_id="HA-2",
        snapshot_sha256=snap,
        requester="factory",
        approver="human",
        decision="ACCEPT",
        expires_at=time.time()+60,
    )
    guard=HumanAcceptanceReplayGuard()
    assert guard.consume(valid,current_snapshot_sha256=snap)
    assert not guard.consume(valid,current_snapshot_sha256=snap)


def test_human_acceptance_rejects_expired_or_non_accept_decision():
    snap=snapshot_hash(commit_sha="abc123",manifest={"x":1})
    expired=HumanAcceptance("HA-3",snap,"factory","human","ACCEPT",1.0)
    denied=HumanAcceptance("HA-4",snap,"factory","human","DENY",time.time()+60)
    assert not verify_human_acceptance(expired,current_snapshot_sha256=snap,now=2.0)
    assert not verify_human_acceptance(denied,current_snapshot_sha256=snap)
