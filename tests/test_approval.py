import time
from father_fua.approval import Approval, ApprovalReplayGuard, action_hash, verify_approval


def test_approval_bound_to_action_and_expiry():
    a = Approval(action_hash("tool.admin"),"human","APPROVE",time.time()+60)
    assert verify_approval(a,"tool.admin") is True
    assert verify_approval(a,"tool.other") is False



def test_approval_rejects_same_requester_and_approver():
    a = Approval(
        action_hash("tool.admin"),
        "alice",
        "APPROVE",
        time.time()+60,
        requester="alice",
        approval_id="A1",
    )
    assert verify_approval(a,"tool.admin",requester="alice") is False


def test_approval_is_single_use_when_replay_guarded():
    a = Approval(
        action_hash("tool.admin"),
        "bob",
        "APPROVE",
        time.time()+60,
        requester="alice",
        approval_id="A2",
    )
    guard=ApprovalReplayGuard()
    assert guard.consume(a,"tool.admin",requester="alice") is True
    assert guard.consume(a,"tool.admin",requester="alice") is False


def test_approval_rejects_requester_mismatch():
    a = Approval(
        action_hash("tool.admin"),
        "bob",
        "APPROVE",
        time.time()+60,
        requester="alice",
        approval_id="A3",
    )
    assert verify_approval(a,"tool.admin",requester="mallory") is False



def test_approval_is_bound_to_payload():
    payload={"target":"prod","version":"1.2.3"}
    a = Approval(
        action_hash("release.production",payload),
        "bob",
        "APPROVE",
        time.time()+60,
        requester="alice",
        approval_id="A4",
    )
    assert verify_approval(
        a,
        "release.production",
        requester="alice",
        payload=payload,
    ) is True
    assert verify_approval(
        a,
        "release.production",
        requester="alice",
        payload={"target":"prod","version":"9.9.9"},
    ) is False
