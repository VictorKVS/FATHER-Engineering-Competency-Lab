from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field


def snapshot_hash(*, commit_sha: str, manifest: dict) -> str:
    if not commit_sha:
        raise ValueError("commit_sha must be non-empty")
    envelope={"commit_sha":commit_sha,"manifest":manifest}
    raw=json.dumps(envelope,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class HumanAcceptance:
    acceptance_id: str
    snapshot_sha256: str
    requester: str
    approver: str
    decision: str
    expires_at: float


def verify_human_acceptance(
    acceptance: HumanAcceptance,
    *,
    current_snapshot_sha256: str,
    now: float | None = None,
) -> bool:
    current=time.time() if now is None else now
    if not acceptance.acceptance_id:
        return False
    if acceptance.decision != "ACCEPT":
        return False
    if acceptance.requester == acceptance.approver:
        return False
    if acceptance.expires_at < current:
        return False
    if acceptance.snapshot_sha256 != current_snapshot_sha256:
        return False
    return True


@dataclass
class HumanAcceptanceReplayGuard:
    consumed_ids: set[str] = field(default_factory=set)

    def consume(
        self,
        acceptance: HumanAcceptance,
        *,
        current_snapshot_sha256: str,
        now: float | None = None,
    ) -> bool:
        if acceptance.acceptance_id in self.consumed_ids:
            return False
        if not verify_human_acceptance(
            acceptance,
            current_snapshot_sha256=current_snapshot_sha256,
            now=now,
        ):
            return False
        self.consumed_ids.add(acceptance.acceptance_id)
        return True
