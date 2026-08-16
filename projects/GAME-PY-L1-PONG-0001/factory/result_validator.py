"""Validate completed experiment records before any A/B interpretation."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
COUNT_METRICS = (
    "critical_defects", "defects_before_green", "repeated_anti_patterns",
    "architecture_deviations", "security_findings", "non_test_source_lines",
)
RATIO_METRICS = ("first_pass_acceptance", "test_completeness", "required_transition_coverage")


def _required(mapping: dict[str, Any], names: list[str], label: str) -> None:
    missing = [name for name in names if mapping.get(name) is None or mapping.get(name) == ""]
    if missing:
        raise ValueError(f"missing {label}: {', '.join(missing)}")


def _timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO timestamp")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO timestamp") from exc


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("contract_id") != "EXP-RESULT-CONTRACT-0001":
        raise ValueError("unexpected result contract")
    if contract.get("expected_arms") != {"baseline": "EXP-BREAKOUT-A1", "treatment": "EXP-BREAKOUT-B1"}:
        raise ValueError("arm contract drift")
    if contract.get("fixed_budget") != {"wall_clock_minutes": 45, "max_iterations": 3, "network_enabled": False}:
        raise ValueError("fixed budget drift")
    if contract.get("parameter_training_performed") is not False:
        raise ValueError("contextual experiment cannot claim parameter training")


def validate_result(result: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    validate_contract(contract)
    arm = result.get("arm")
    expected_id = contract["expected_arms"].get(arm)
    if expected_id is None or result.get("experiment_id") != expected_id:
        raise ValueError("experiment ID/arm mismatch")
    if result.get("status") != "completed":
        raise ValueError("result status must be completed")
    if result.get("parameter_training_performed") is not False:
        raise ValueError("parameter training would invalidate this contextual pair")

    runner = result.get("runner", {})
    _required(runner, contract["required_runner_fields"], "runner identity")
    budget = result.get("budget", {})
    for name, expected in contract["fixed_budget"].items():
        if budget.get(name) != expected:
            raise ValueError(f"budget mismatch: {name}")
    for name in ("token_input", "token_output"):
        value = budget.get(name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")

    preflight = result.get("preflight", {})
    if not SHA256.fullmatch(str(preflight.get("inventory_sha256", ""))):
        raise ValueError("invalid inventory SHA-256")
    if not SHA256.fullmatch(str(preflight.get("packet_sha256", ""))):
        raise ValueError("invalid packet SHA-256")
    if preflight.get("contamination_check") != "passed":
        raise ValueError("contamination preflight did not pass")

    timing = result.get("timing", {})
    started = _timestamp(timing.get("started_at"), "started_at")
    first_test = _timestamp(timing.get("first_test_run_at"), "first_test_run_at")
    green = _timestamp(timing.get("green_at"), "green_at")
    if not started <= first_test <= green:
        raise ValueError("timestamps are not monotonic")
    minutes = timing.get("time_to_green_minutes")
    if isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or not 0 <= minutes <= 45:
        raise ValueError("time_to_green_minutes must be in [0, 45]")

    metrics = result.get("metrics", {})
    _required(metrics, contract["required_metrics"], "metrics")
    for name in COUNT_METRICS:
        value = metrics[name]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    for name in RATIO_METRICS:
        value = metrics[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be in [0, 1]")
    if metrics["non_test_source_lines"] > 350:
        raise ValueError("non-test source line budget exceeded")

    evidence = result.get("evidence", {})
    _required(evidence, contract["required_evidence"], "evidence")
    if not GIT_SHA.fullmatch(str(evidence["source_commit"])):
        raise ValueError("invalid source commit")
    passed, total = evidence["tests_passed"], evidence["tests_total"]
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (passed, total)) or total <= 0 or not 0 <= passed <= total:
        raise ValueError("invalid test counts")
    if evidence["compileall"] != "passed":
        raise ValueError("compileall evidence must pass")
    if not isinstance(evidence["review_ids"], list):
        raise ValueError("review_ids must be a list")
    if result.get("decision") == "accepted" and (passed != total or metrics["critical_defects"] != 0):
        raise ValueError("accepted result requires all tests and zero critical defects")
    return {"decision": "result_valid", "experiment_id": expected_id, "arm": arm, "context_instance_id": runner["context_instance_id"]}


def validate_pair(baseline: dict[str, Any], treatment: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    a, b = validate_result(baseline, contract), validate_result(treatment, contract)
    ar, br = baseline["runner"], treatment["runner"]
    for name in ("provider", "model", "version"):
        if ar[name] != br[name]:
            raise ValueError(f"runner mismatch: {name}")
    if ar["context_instance_id"] == br["context_instance_id"]:
        raise ValueError("paired arms require distinct context IDs")
    if baseline["preflight"]["packet_sha256"] == treatment["preflight"]["packet_sha256"]:
        raise ValueError("paired arms require distinct packet hashes")
    for name in contract["fixed_budget"]:
        if baseline["budget"][name] != treatment["budget"][name]:
            raise ValueError(f"pair budget mismatch: {name}")
    return {
        "decision": "pair_valid_for_evaluation",
        "baseline": a["experiment_id"],
        "treatment": b["experiment_id"],
        "runner_identity_equal": True,
        "contexts_distinct": True,
        "learning_claim": "single paired observation only",
        "role_promotion": "not_evaluated",
        "parameter_training_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate FATHER experiment results")
    sub = parser.add_subparsers(dest="command", required=True)
    contract_cmd = sub.add_parser("contract")
    contract_cmd.add_argument("contract", type=Path)
    result_cmd = sub.add_parser("result")
    result_cmd.add_argument("contract", type=Path); result_cmd.add_argument("result", type=Path)
    pair_cmd = sub.add_parser("pair")
    pair_cmd.add_argument("contract", type=Path); pair_cmd.add_argument("baseline", type=Path); pair_cmd.add_argument("treatment", type=Path)
    args = parser.parse_args(argv)
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    if args.command == "contract":
        validate_contract(contract); output = {"decision": "contract_valid", "contract_id": contract["contract_id"]}
    elif args.command == "result":
        output = validate_result(json.loads(args.result.read_text(encoding="utf-8")), contract)
    else:
        output = validate_pair(json.loads(args.baseline.read_text(encoding="utf-8")), json.loads(args.treatment.read_text(encoding="utf-8")), contract)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
