from __future__ import annotations

from dataclasses import dataclass, replace


ORDER = (
    "DETECTED",
    "CONTAINED",
    "EVIDENCE_PRESERVED",
    "INVESTIGATED",
    "RECOVERED",
    "CORRECTED",
    "RECERTIFIED",
    "CLOSED",
)


@dataclass(frozen=True)
class Incident:
    incident_id: str
    stage: str = "DETECTED"


def advance(incident: Incident, next_stage: str) -> Incident:
    if next_stage not in ORDER:
        raise ValueError("invalid incident stage")
    current_index=ORDER.index(incident.stage)
    next_index=ORDER.index(next_stage)
    if next_index != current_index + 1:
        raise ValueError("incident stages must advance sequentially")
    return replace(incident,stage=next_stage)


def close_allowed(incident: Incident) -> bool:
    return incident.stage=="CLOSED"
