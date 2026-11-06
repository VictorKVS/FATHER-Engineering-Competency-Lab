from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class CandidateResult:
    model_id: str
    status: str
    score: int
    latency_ms: int
    payload: dict[str, Any]
    hard_fails: tuple[str, ...] = ()


class ModelSwapRouter:
    """Generic model-selection chassis. It knows nothing about stories."""

    def __init__(self, pass_threshold: int = 80) -> None:
        self.pass_threshold = pass_threshold

    def select(
        self,
        candidates: list[dict[str, Any]],
        execute: Callable[[dict[str, Any]], dict[str, Any]],
        evaluate: Callable[[dict[str, Any]], tuple[int, list[str]]],
    ) -> tuple[CandidateResult | None, list[CandidateResult]]:
        results: list[CandidateResult] = []

        for candidate in candidates:
            model_id = candidate["id"]
            try:
                record = execute(candidate)
                score, hard_fails = evaluate(record)
                result = CandidateResult(
                    model_id=model_id,
                    status="PASS" if score >= self.pass_threshold and not hard_fails else "FAIL",
                    score=score,
                    latency_ms=int(record.get("latency_ms", 0)),
                    payload=record,
                    hard_fails=tuple(hard_fails),
                )
            except Exception as exc:
                result = CandidateResult(
                    model_id=model_id,
                    status="RUNTIME_FAIL",
                    score=0,
                    latency_ms=0,
                    payload={"error": repr(exc)},
                    hard_fails=("runtime_fail",),
                )
            results.append(result)

            if result.status == "PASS":
                return result, results

        return None, results

    @staticmethod
    def leaderboard(results: list[CandidateResult]) -> list[CandidateResult]:
        return sorted(
            results,
            key=lambda r: (
                r.status != "PASS",
                -r.score,
                r.latency_ms if r.latency_ms > 0 else 10**12,
                r.model_id,
            ),
        )
