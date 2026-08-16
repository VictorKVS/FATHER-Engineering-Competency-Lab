"""Evaluate paired baseline/treatment transfer trials without claiming training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import fmean
from typing import Any

LOWER_IS_BETTER = (
    "critical_defects",
    "time_to_green_minutes",
    "architecture_deviations",
)
HIGHER_IS_BETTER = ("first_pass_acceptance", "test_completeness")
METRICS = LOWER_IS_BETTER + HIGHER_IS_BETTER


def evaluate_transfer(record: dict[str, Any]) -> dict[str, Any]:
    trials = record.get("trials", [])
    minimum_pairs = int(record.get("minimum_pairs", 3))
    if len(trials) < minimum_pairs:
        return {
            "decision": "insufficient_data",
            "pairs_observed": len(trials),
            "minimum_pairs": minimum_pairs,
            "improved_metrics": [],
        }

    means: dict[str, dict[str, float]] = {"baseline": {}, "treatment": {}}
    for arm in means:
        for metric in METRICS:
            values = [trial[arm][metric] for trial in trials]
            if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
                raise ValueError(f"{arm}.{metric} must be numeric")
            means[arm][metric] = fmean(values)

    improved = [
        metric for metric in LOWER_IS_BETTER
        if means["treatment"][metric] < means["baseline"][metric]
    ] + [
        metric for metric in HIGHER_IS_BETTER
        if means["treatment"][metric] > means["baseline"][metric]
    ]
    critical_not_worse = (
        means["treatment"]["critical_defects"]
        <= means["baseline"]["critical_defects"]
    )
    decision = "promote_candidate" if critical_not_worse and len(improved) >= 2 else "reject"
    return {
        "decision": decision,
        "pairs_observed": len(trials),
        "minimum_pairs": minimum_pairs,
        "improved_metrics": improved,
        "critical_defects_not_worse": critical_not_worse,
        "means": means,
        "caveat": "Candidate promotion only; independent review is still required.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a FATHER paired transfer record")
    parser.add_argument("record", type=Path)
    args = parser.parse_args(argv)
    result = evaluate_transfer(json.loads(args.record.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] != "reject" else 1


if __name__ == "__main__":
    raise SystemExit(main())
