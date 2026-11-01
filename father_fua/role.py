from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    primary_role: str
    allowed_duties: tuple[str,...]
    forbidden_duties: tuple[str,...]
    jurisdiction: tuple[str,...]


def authorize_duty(role: Role, duty: str) -> bool:
    if duty in role.forbidden_duties:
        return False
    return duty in role.allowed_duties
