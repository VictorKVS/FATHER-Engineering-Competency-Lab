from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


@dataclass(frozen=True)
class GateDecision:
    decision: str
    decided_by: str
    reason: str | None = None


class IdeaIntakeEngine:
    MIN_LENGTH = 20

    def __init__(self, evidence_root: str | Path = ".father/stage_000") -> None:
        self.evidence_root = Path(evidence_root)
        self.evidence_root.mkdir(parents=True, exist_ok=True)

    def input_test(self, payload: dict[str, Any]) -> dict[str, Any]:
        idea = str(payload.get("raw_idea") or "").strip()
        failures: list[str] = []
        if not idea:
            failures.append("raw_idea_empty")
        elif len(idea) < self.MIN_LENGTH:
            failures.append("raw_idea_too_short")

        return {
            "status": "PASS" if not failures else "FAIL",
            "failures": failures,
            "checks": {
                "raw_idea_not_empty": bool(idea),
                "raw_idea_has_meaningful_length": len(idea) >= self.MIN_LENGTH,
            },
        }

    def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        test = self.input_test(payload)
        if test["status"] != "PASS":
            raise ValueError(f"Stage 000 input invalid: {test['failures']}")

        idea = str(payload["raw_idea"]).strip()
        context = list(payload.get("known_context") or [])
        constraints = list(payload.get("known_constraints") or [])

        facts = [{"statement": "Raw idea was supplied by the user.", "source": "input.raw_idea"}]
        if context:
            facts.append({"statement": "Known context was supplied.", "source": "input.known_context"})
        if constraints:
            facts.append({"statement": "Known constraints were supplied.", "source": "input.known_constraints"})

        return {
            "original_idea": idea,
            "normalized_intent": idea,
            "problem_statement": "",
            "expected_outcome": "",
            "facts": facts,
            "assumptions": [],
            "unknowns": [
                "Who is the primary user/customer?",
                "What measurable outcome defines success?",
                "Which constraints are HARD?",
            ],
            "initial_risks": [],
            "first_questions": [
                "What problem must the product solve?",
                "Who accepts the result?",
                "What must be true before Stage 001 is allowed?",
            ],
            "recommended_next_step": "HUMAN_REVIEW_STAGE_000",
        }

    def artifact_test(self, analysis: dict[str, Any]) -> dict[str, Any]:
        failures: list[str] = []
        if not analysis.get("original_idea"):
            failures.append("original_idea_missing")
        if not isinstance(analysis.get("facts"), list):
            failures.append("facts_invalid")
        if not isinstance(analysis.get("assumptions"), list):
            failures.append("assumptions_invalid")
        if not isinstance(analysis.get("unknowns"), list):
            failures.append("unknowns_invalid")
        if not analysis.get("recommended_next_step"):
            failures.append("recommended_next_step_missing")

        return {"status": "PASS" if not failures else "FAIL", "failures": failures}

    def make_run(self, payload: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        record = {
            "stage_id": "STAGE-000",
            "run_id": run_id,
            "state": "READY_FOR_GATE",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "input_snapshot": payload,
            "input_test": self.input_test(payload),
            "analysis": analysis,
            "artifact_test": self.artifact_test(analysis),
            "human_gate": {"decision": None, "decided_by": None, "decided_at": None, "reason": None},
            "project_creation_proposal": None,
        }
        self._write(record)
        return record

    def apply_gate(self, record: dict[str, Any], gate: GateDecision) -> dict[str, Any]:
        if gate.decision not in {"APPROVE", "HOLD", "REJECT"}:
            raise ValueError("Unsupported gate decision")
        if gate.decision in {"HOLD", "REJECT"} and not (gate.reason or "").strip():
            raise ValueError("Reason is required for HOLD/REJECT")
        if record["input_test"]["status"] != "PASS" or record["artifact_test"]["status"] != "PASS":
            raise ValueError("Cannot gate an invalid stage")

        record = dict(record)
        record["human_gate"] = {
            "decision": gate.decision,
            "decided_by": gate.decided_by,
            "decided_at": datetime.now(timezone.utc).isoformat(),
            "reason": gate.reason,
        }

        if gate.decision == "APPROVE":
            record["state"] = "APPROVED"
            record["project_creation_proposal"] = {
                "stage": "STAGE-001",
                "mode": "PROPOSAL_ONLY",
                "project_id": "PENDING",
                "github_repository": "PENDING_APPROVAL",
                "local_directory": "PENDING_APPROVAL",
                "note": "No repository or local project has been created by Stage 000.",
            }
        elif gate.decision == "HOLD":
            record["state"] = "HOLD"
        else:
            record["state"] = "REJECTED"

        self._write(record)
        return record

    def _write(self, record: dict[str, Any]) -> None:
        path = self.evidence_root / f"{record['run_id']}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
