from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Approval:
    action_hash: str
    approver: str
    decision: str
    expires_at: float


def action_hash(action: str) -> str:
    return hashlib.sha256(action.encode()).hexdigest()


def verify_approval(approval: Approval, action: str, *, now: float | None = None) -> bool:
    now = now or time.time()
    return (
        approval.decision == "APPROVE"
        and approval.action_hash == action_hash(action)
        and approval.expires_at >= now
    )
