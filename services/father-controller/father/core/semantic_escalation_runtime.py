import time
from copy import deepcopy
from pathlib import Path

from father.core.escalating_runtime import EscalatingRuntime
from father.core.semantic_acceptance_gate import SemanticAcceptanceGate


class SemanticEscalationRuntime:
    """MVP-07: runtime execution with semantic acceptance and escalation."""

    def __init__(self, base_dir, judge_brain_id="qwen-analysis"):
        self.base = Path(base_dir)
        self.executor = EscalatingRuntime(self.base)
        self.semantic = SemanticAcceptanceGate(self.base, judge_brain_id=judge_brain_id)

    def _semantic_check(self, task, result, source_context, source_claims):
        return self.semantic.evaluate(
            task=task.get("text", ""),
            answer=str(result.get("content") or ""),
            source_context=source_context,
            source_claims=source_claims,
        )

    def run(self, task, product_spec, source_context, source_claims, gpu_temp_c=None):
        first = self.executor._execute(task, product_spec, gpu_temp_c=gpu_temp_c)
        if not first.get("ok"):
            return {
                "ok": False,
                "status": "EXECUTION_FAILED",
                "reason": "initial_execution_failed",
                "attempts": [first],
            }

        first_semantic = self._semantic_check(
            task, first["result"], source_context, source_claims
        )
        attempts = [{
            **first["telemetry"],
            "semantic": first_semantic,
        }]

        if first_semantic.get("accepted"):
            return {
                "ok": True,
                "status": "ACCEPTED",
                "escalated": False,
                "initial_brain": first["result"].get("brain_id"),
                "final_brain": first["result"].get("brain_id"),
                "final_result": first["result"],
                "attempts": attempts,
                "escalation_reason": [],
            }

        role = (first["plan"].get("role") or
                (first["plan"].get("role_plan") or {}).get("profile", {}).get("role"))
        if role != "text_analyst" or first["result"].get("brain_id") != "qwen-analysis-fast":
            return {
                "ok": False,
                "status": "SEMANTIC_REJECTED",
                "reason": "no_approved_semantic_escalation_path",
                "escalated": False,
                "attempts": attempts,
                "escalation_reason": first_semantic,
            }

        escalated_task = deepcopy(task)
        escalated_task["role"] = "text_analyst"
        escalated_task["complexity"] = max(3, int(task.get("complexity", 2)))
        second = self.executor._execute(
            escalated_task, product_spec, gpu_temp_c=gpu_temp_c
        )
        if not second.get("ok"):
            return {
                "ok": False,
                "status": "ESCALATION_EXECUTION_FAILED",
                "reason": "escalated_execution_failed",
                "escalated": True,
                "initial_brain": first["result"].get("brain_id"),
                "attempts": attempts + [second],
                "escalation_reason": first_semantic,
            }

        second_semantic = self._semantic_check(
            escalated_task, second["result"], source_context, source_claims
        )
        attempts.append({
            **second["telemetry"],
            "semantic": second_semantic,
        })

        accepted = bool(second["result"].get("ok") and second_semantic.get("accepted"))
        return {
            "ok": accepted,
            "status": "ACCEPTED" if accepted else "ESCALATION_EXHAUSTED",
            "reason": None if accepted else "final_semantic_acceptance_failed",
            "escalated": True,
            "initial_brain": first["result"].get("brain_id"),
            "final_brain": second["result"].get("brain_id"),
            "final_result": second["result"],
            "attempts": attempts,
            "escalation_reason": first_semantic,
            "final_semantic": second_semantic,
        }
