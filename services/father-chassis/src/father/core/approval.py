from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from uuid import uuid4


class ApprovalRequired(PermissionError):
    def __init__(self, approval_id: str, action: str) -> None:
        self.approval_id = approval_id
        self.action = action
        super().__init__(f"human approval required for action {action}; approval_id={approval_id}")


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    approval_id: str
    trace_id: str
    action: str
    status: str


class HumanApprovalGate:
    def __init__(self, required_actions: set[str] | None = None) -> None:
        self.required_actions = set(required_actions or set())
        self._records: dict[str, ApprovalRecord] = {}
        self._lock = RLock()

    def check(self, *, trace_id: str, action: str, approval_id: str | None = None) -> None:
        if action not in self.required_actions:
            return
        with self._lock:
            if approval_id:
                rec = self._records.get(approval_id)
                if rec and rec.action == action and rec.status == "approved":
                    return
                raise PermissionError(f"invalid or unapproved approval_id for action {action}")
            new_id = str(uuid4())
            self._records[new_id] = ApprovalRecord(new_id, trace_id, action, "pending")
        raise ApprovalRequired(new_id, action)

    def approve(self, approval_id: str) -> ApprovalRecord:
        with self._lock:
            rec = self._records[approval_id]
            approved = ApprovalRecord(rec.approval_id, rec.trace_id, rec.action, "approved")
            self._records[approval_id] = approved
            return approved

    def get(self, approval_id: str) -> ApprovalRecord:
        return self._records[approval_id]
