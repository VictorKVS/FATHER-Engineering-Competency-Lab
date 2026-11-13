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
    NAMESPACE = "approval_gate"

    def __init__(self, required_actions: set[str] | None = None, store=None) -> None:
        self.required_actions = set(required_actions or set())
        self.store = store
        self._records: dict[str, ApprovalRecord] = {}
        self._lock = RLock()

    def _save(self, record: ApprovalRecord) -> None:
        self._records[record.approval_id] = record
        if self.store is not None:
            self.store.set(
                self.NAMESPACE,
                record.approval_id,
                {
                    "approval_id": record.approval_id,
                    "trace_id": record.trace_id,
                    "action": record.action,
                    "status": record.status,
                },
            )

    def _load(self, approval_id: str) -> ApprovalRecord | None:
        record = self._records.get(approval_id)
        if record is not None:
            return record
        if self.store is None:
            return None
        raw = self.store.get(self.NAMESPACE, approval_id)
        if raw is None:
            return None
        record = ApprovalRecord(
            approval_id=str(raw["approval_id"]),
            trace_id=str(raw["trace_id"]),
            action=str(raw["action"]),
            status=str(raw["status"]),
        )
        self._records[approval_id] = record
        return record

    def check(self, *, trace_id: str, action: str, approval_id: str | None = None) -> None:
        if action not in self.required_actions:
            return
        with self._lock:
            if approval_id:
                rec = self._load(approval_id)
                if rec and rec.action == action and rec.status == "approved":
                    return
                raise PermissionError(f"invalid or unapproved approval_id for action {action}")
            new_id = str(uuid4())
            self._save(ApprovalRecord(new_id, trace_id, action, "pending"))
        raise ApprovalRequired(new_id, action)

    def request(self, *, trace_id: str, action: str) -> ApprovalRecord:
        with self._lock:
            new_id = str(uuid4())
            record = ApprovalRecord(new_id, trace_id, action, "pending")
            self._save(record)
            return record

    def approve(self, approval_id: str) -> ApprovalRecord:
        with self._lock:
            rec = self._load(approval_id)
            if rec is None:
                raise KeyError(approval_id)
            approved = ApprovalRecord(rec.approval_id, rec.trace_id, rec.action, "approved")
            self._save(approved)
            return approved

    def get(self, approval_id: str) -> ApprovalRecord:
        record = self._load(approval_id)
        if record is None:
            raise KeyError(approval_id)
        return record
