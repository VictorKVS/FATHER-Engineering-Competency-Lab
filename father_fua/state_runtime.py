from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    revision: int
    session_id: str
    status: str


def transition(state: State, new_status: str) -> State:
    return replace(state, revision=state.revision+1, status=new_status)


def state_hash(state: State) -> str:
    raw=json.dumps(state.__dict__,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()
