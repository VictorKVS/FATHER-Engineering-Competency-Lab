from __future__ import annotations

from typing import Any


REQUIRED_CONTINUITY = ("pov", "tense", "characters", "open_threads_used")


def evaluate_story_record(record: dict[str, Any]) -> tuple[int, list[str]]:
    output = record.get("output") or {}
    hard_fails: list[str] = []
    score = 0

    if record.get("contract_valid"):
        score += 30
    else:
        hard_fails.append("output_contract_invalid")

    continuation = output.get("continuation")
    if isinstance(continuation, str) and continuation.strip():
        score += 20
    else:
        hard_fails.append("continuation_empty")

    continuity = output.get("continuity")
    if isinstance(continuity, dict):
        present = sum(1 for key in REQUIRED_CONTINUITY if key in continuity)
        score += round(20 * present / len(REQUIRED_CONTINUITY))
        if present != len(REQUIRED_CONTINUITY):
            hard_fails.append("continuity_object_incomplete")
    else:
        hard_fails.append("continuity_object_missing")

    if isinstance(output.get("canon_delta"), list) and isinstance(output.get("proposals"), list):
        score += 10
    else:
        if not isinstance(output.get("canon_delta"), list):
            hard_fails.append("canon_delta_not_array")
        if not isinstance(output.get("proposals"), list):
            hard_fails.append("proposals_not_array")

    if isinstance(output.get("model_id"), str) and output.get("model_id"):
        score += 10
    else:
        hard_fails.append("model_id_missing")

    target = int((record.get("input") or {}).get("target_length") or 0)
    words = len(continuation.split()) if isinstance(continuation, str) else 0
    if target <= 0 or (words >= max(20, int(target * 0.35)) and words <= int(target * 1.8)):
        score += 10

    return min(score, 100), hard_fails
