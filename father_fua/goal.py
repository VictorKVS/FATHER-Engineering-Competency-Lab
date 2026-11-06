from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Goal:
    mission: str
    success_criteria: tuple[str,...]
    failure_criteria: tuple[str,...]
    constraints: tuple[str,...]
    priority: int
    ttl_seconds: int


def create_goal(mission: str, *, success: list[str], failure: list[str], constraints: list[str] | None=None, priority: int=50, ttl_seconds: int=600) -> Goal:
    if not mission or not success or not failure:
        raise ValueError("mission, success and failure criteria required")
    if ttl_seconds <= 0 or not 0 <= priority <= 100:
        raise ValueError("invalid goal bounds")
    return Goal(mission,tuple(success),tuple(failure),tuple(constraints or []),priority,ttl_seconds)
