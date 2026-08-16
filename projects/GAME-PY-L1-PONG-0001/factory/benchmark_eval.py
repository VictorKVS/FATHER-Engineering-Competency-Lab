"""Validate BENCH-GAME-10 and evaluate task evidence without promoting roles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def validate_catalog(catalog: dict[str, Any]) -> None:
    tasks = catalog["tasks"]
    if len(tasks) != 10 or [task["level"] for task in tasks] != list(range(1, 11)):
        raise ValueError("catalog must contain exactly ordered levels 1..10")
    if len({task["task_id"] for task in tasks}) != 10:
        raise ValueError("task IDs must be unique")
    dimensions = set(catalog["dimensions"])
    for role, weights in catalog["role_weights"].items():
        if set(weights) != dimensions:
            raise ValueError(f"{role} weights must cover every dimension")
        if abs(sum(weights.values()) - 1.0) > 1e-9:
            raise ValueError(f"{role} weights must sum to 1")
    for task in tasks:
        if set(task["checkpoints"]) != {"minimum", "standard", "stretch"}:
            raise ValueError(f"{task['task_id']} must define three checkpoints")


def evaluate_attempt(catalog: dict[str, Any], attempt: dict[str, Any]) -> dict[str, Any]:
    validate_catalog(catalog)
    task = next((item for item in catalog["tasks"] if item["task_id"] == attempt.get("task_id")), None)
    if task is None:
        raise ValueError("attempt task_id is not in catalog")
    evidence = attempt.get("evidence", {})
    dimension_scores = attempt.get("dimension_scores", {})
    if set(dimension_scores) != set(catalog["dimensions"]):
        raise ValueError("attempt must score every dimension")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1 for v in dimension_scores.values()):
        raise ValueError("dimension scores must be numeric values in [0, 1]")

    role_scores = {
        role: sum(dimension_scores[name] * weight for name, weight in weights.items())
        for role, weights in catalog["role_weights"].items()
    }
    score_floor = min(role_scores.values())
    critical_clear = attempt.get("critical_defects", 0) == 0
    achieved = "none"
    cumulative: list[str] = []
    for checkpoint in ("minimum", "standard", "stretch"):
        cumulative.extend(task["checkpoints"][checkpoint])
        threshold = catalog["checkpoint_thresholds"][checkpoint]
        if critical_clear and score_floor >= threshold and all(evidence.get(key) is True for key in cumulative):
            achieved = checkpoint
        else:
            break
    return {
        "benchmark_id": catalog["benchmark_id"],
        "task_id": task["task_id"],
        "task_level": task["level"],
        "achieved_checkpoint": achieved,
        "role_scores": role_scores,
        "score_floor": score_floor,
        "critical_defects_clear": critical_clear,
        "role_promotion": "not_evaluated",
        "learning_claim": "operational evidence only; no parameter-training claim",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a BENCH-GAME-10 attempt")
    parser.add_argument("catalog", type=Path)
    parser.add_argument("attempt", type=Path)
    args = parser.parse_args(argv)
    result = evaluate_attempt(
        json.loads(args.catalog.read_text(encoding="utf-8")),
        json.loads(args.attempt.read_text(encoding="utf-8")),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
