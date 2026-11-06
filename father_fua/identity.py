from __future__ import annotations
import hashlib, json, uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    agent_id: str
    instance_id: str
    version: str
    owner: str
    trust_level: str
    manifest_sha256: str


def create_identity(*, agent_id: str, version: str, owner: str, trust_level: str) -> Identity:
    if trust_level not in {"UNTRUSTED","RESTRICTED","STANDARD","PRIVILEGED"}:
        raise ValueError("invalid trust level")
    payload={"agent_id":agent_id,"version":version,"owner":owner,"trust_level":trust_level}
    raw=json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
    return Identity(agent_id,str(uuid.uuid4()),version,owner,trust_level,hashlib.sha256(raw).hexdigest())
