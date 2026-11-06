from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    task_id: str
    goal_link: str
    action: str
    dependencies: tuple[str,...]=()


def make_plan(goal_id: str, mission: str) -> list[Task]:
    if not goal_id:
        raise ValueError("goal link required")
    return [Task("T1",goal_id,"research"),Task("T2",goal_id,"respond",("T1",))]


def validate_plan(tasks: list[Task]) -> bool:
    ids={t.task_id for t in tasks}
    return all(t.goal_link and all(d in ids for d in t.dependencies) for t in tasks)
