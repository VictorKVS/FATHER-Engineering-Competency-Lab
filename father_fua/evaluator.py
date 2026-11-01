from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class CriterionResult:
    criterion_id: str
    status: str
    evidence: str | None = None
    category: str = "QUALITY"


@dataclass(frozen=True)
class EvaluationSummary:
    status: str
    passed: int
    failed: int
    blocked: int


class Evaluator:
    def summarize(self, results: list[CriterionResult]) -> EvaluationSummary:
        failed = sum(1 for r in results if r.status == "FAIL")
        blocked = sum(1 for r in results if r.status in {"NOT_RUN", "BLOCKED"} or not r.evidence)
        passed = sum(1 for r in results if r.status == "PASS" and r.evidence)
        if failed:
            status = "FAIL"
        elif blocked:
            status = "BLOCKED"
        else:
            status = "PASS"
        return EvaluationSummary(status=status, passed=passed, failed=failed, blocked=blocked)
