from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Approval:
    action_hash: str
    approver: str
    decision: str
    expires_at: float
    requester: str = ""
    approval_id: str = ""


def action_hash(action: str, payload: dict | None = None) -> str:
    envelope={"action":action,"payload":payload}
    raw=json.dumps(envelope,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def verify_approval(
    approval: Approval,
    action: str,
    *,
    now: float | None = None,
    requester: str | None = None,
    payload: dict | None = None,
) -> bool:
    current = time.time() if now is None else now
    if approval.decision != "APPROVE":
        return False
    if approval.action_hash != action_hash(action,payload):
        return False
    if approval.expires_at < current:
        return False
    if requester is not None:
        if approval.requester and approval.requester != requester:
            return False
        if approval.approver == requester:
            return False
    return True


@dataclass
class ApprovalReplayGuard:
    consumed_ids: set[str] = field(default_factory=set)

    def consume(
        self,
        approval: Approval,
        action: str,
        *,
        requester: str,
        now: float | None = None,
        payload: dict | None = None,
    ) -> bool:
        if not approval.approval_id:
            return False
        if approval.approval_id in self.consumed_ids:
            return False
        if not verify_approval(
            approval,
            action,
            now=now,
            requester=requester,
            payload=payload,
        ):
            return False
        self.consumed_ids.add(approval.approval_id)
        return True
