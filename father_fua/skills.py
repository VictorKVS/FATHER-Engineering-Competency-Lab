from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    skill_id: str
    version: str
    capabilities: tuple[str, ...]
    dependencies: tuple[str, ...] = ()


class SkillRegistry:
    def __init__(self) -> None:
        self.skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if not skill.version:
            raise ValueError("version required")
        missing = [d for d in skill.dependencies if d not in self.skills]
        if missing:
            raise ValueError(f"missing dependencies: {missing}")
        self.skills[skill.skill_id] = skill

    def find(self, capability: str) -> list[Skill]:
        return [s for s in self.skills.values() if capability in s.capabilities]
