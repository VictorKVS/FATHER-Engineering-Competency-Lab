from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Callable
import time
import uuid


@dataclass(frozen=True)
class AgentConstruct:
    agent_id: str
    purpose: str
    domain: str
    role_version: str
    prompt_version: str
    rag_version: str
    knowledge_snapshot: str
    input_contract: str
    output_contract: str
    eval_profile: str
    pass_threshold: int
    hard_fail_rules: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentConstruct":
        root = payload.get("agent", payload)
        identity = root["identity"]
        intelligence = root["intelligence"]
        contracts = root["contracts"]
        evaluation = root["evaluation"]
        return cls(
            agent_id=identity["agent_id"],
            purpose=identity["purpose"],
            domain=identity["domain"],
            role_version=intelligence["role_version"],
            prompt_version=intelligence["prompt_version"],
            rag_version=intelligence["rag_version"],
            knowledge_snapshot=intelligence["knowledge_snapshot"],
            input_contract=contracts["input_contract"],
            output_contract=contracts["output_contract"],
            eval_profile=evaluation["eval_profile"],
            pass_threshold=int(evaluation.get("pass_threshold", 80)),
            hard_fail_rules=tuple(evaluation.get("hard_fail_rules", [])),
        )

    def frozen_context(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "purpose": self.purpose,
            "domain": self.domain,
            "role_version": self.role_version,
            "prompt_version": self.prompt_version,
            "rag_version": self.rag_version,
            "knowledge_snapshot": self.knowledge_snapshot,
            "input_contract": self.input_contract,
            "output_contract": self.output_contract,
            "eval_profile": self.eval_profile,
        }


@dataclass(frozen=True)
class TournamentResult:
    model_id: str
    status: str
    score: float
    latency_ms: float
    hard_fails: tuple[str, ...]
    output: dict[str, Any]
    metrics: dict[str, Any]


class AgentTournamentRunner:
    def __init__(self, construct: AgentConstruct) -> None:
        self.construct = construct

    def run(
        self,
        *,
        task_input: dict[str, Any],
        candidates: list[dict[str, Any]],
        execute: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
        evaluate: Callable[[dict[str, Any], dict[str, Any]], tuple[float, list[str], dict[str, Any]]],
    ) -> dict[str, Any]:
        tournament_id = str(uuid.uuid4())
        started = datetime.now(timezone.utc).isoformat()
        frozen = self.construct.frozen_context()
        results: list[TournamentResult] = []

        for candidate in candidates:
            model_id = candidate["id"]
            context = {
                "agent": frozen,
                "task_input": task_input,
                "model": candidate,
            }
            t0 = time.perf_counter()
            try:
                output = execute(candidate, context)
                latency_ms = round((time.perf_counter() - t0) * 1000, 3)
                score, hard_fails, metrics = evaluate(output, context)
                status = "PASS" if score >= self.construct.pass_threshold and not hard_fails else "FAIL"
            except Exception as exc:
                latency_ms = round((time.perf_counter() - t0) * 1000, 3)
                output = {"error": repr(exc)}
                score = 0.0
                hard_fails = ["runtime_fail"]
                metrics = {"runtime_error": repr(exc)}
                status = "RUNTIME_FAIL"

            results.append(TournamentResult(
                model_id=model_id,
                status=status,
                score=float(score),
                latency_ms=latency_ms,
                hard_fails=tuple(hard_fails),
                output=output,
                metrics=metrics,
            ))

        leaderboard = sorted(
            results,
            key=lambda r: (
                r.status != "PASS",
                -r.score,
                r.latency_ms,
                r.model_id,
            ),
        )
        winner = leaderboard[0] if leaderboard and leaderboard[0].status == "PASS" else None
        completed = datetime.now(timezone.utc).isoformat()

        return {
            "schema": "FATHER_MODEL_TOURNAMENT_V1",
            "tournament_id": tournament_id,
            "agent_id": self.construct.agent_id,
            "frozen_context": frozen,
            "task_input": task_input,
            "started_at": started,
            "completed_at": completed,
            "results": [asdict(r) for r in results],
            "leaderboard": [asdict(r) for r in leaderboard],
            "winner": asdict(winner) if winner else None,
            "status": "PASS" if winner else "HOLD",
        }
