import json
from pathlib import Path

from father.core.semantic_escalation_runtime import SemanticEscalationRuntime

BASE = Path(__file__).resolve().parent

SPEC = {
  "product_id": "father-semantic-escalation-mvp07",
  "agent_manifest": "config/agents/father_general.json",
  "brain_id": "qwen-analysis",
  "competency_id": "generic",
  "inputs": ["api", "file"],
  "outputs": ["json", "file"],
  "knowledge": {"adapter": "folder"},
  "retrieval": {"top_k": 5},
  "tools": "default",
  "context_bus": True,
}

CONTEXT = """FATHER разделяет агента и модель.
Модель является заменяемым Brain-слотом агента.
Совместимая модель выбирается по роли, качеству, скорости, экономике и ограничениям."""

CLAIMS = [
    "FATHER разделяет агента и модель.",
    "Модель является заменяемым Brain-слотом агента.",
    "Совместимая модель выбирается по роли, качеству, скорости, экономике и ограничениям.",
]

def add(rows, name, passed, details):
    rows.append({"name": name, "passed": bool(passed), "details": details})
    print(("PASS" if passed else "FAIL"), name, json.dumps(details, ensure_ascii=False))
    return bool(passed)

def compact(x):
    return {
        "ok": x.get("ok"),
        "status": x.get("status"),
        "escalated": x.get("escalated"),
        "initial_brain": x.get("initial_brain"),
        "final_brain": x.get("final_brain"),
        "reason": x.get("reason"),
        "attempts": [
            {
                "brain_id": a.get("brain_id"),
                "runtime_model": a.get("runtime_model"),
                "latency_ms": a.get("latency_ms"),
                "semantic_status": (a.get("semantic") or {}).get("status"),
                "grounded_semantic_score": (a.get("semantic") or {}).get("grounded_semantic_score"),
                "supported_claims": (a.get("semantic") or {}).get("supported_claims"),
                "contradicted_claims": (a.get("semantic") or {}).get("contradicted_claims"),
            } for a in x.get("attempts", [])
        ],
    }

class ForcedFirstRejectRuntime(SemanticEscalationRuntime):
    """Test-only fault injection: first semantic verdict is rejected once."""
    def __init__(self, base_dir):
        super().__init__(base_dir)
        self._calls = 0

    def _semantic_check(self, task, result, source_context, source_claims):
        self._calls += 1
        real = super()._semantic_check(task, result, source_context, source_claims)
        if self._calls == 1:
            return {
                **real,
                "accepted": False,
                "status": "ESCALATE",
                "fault_injection": "FORCED_FIRST_REJECT",
            }
        return real

def main():
    rows = []
    ok = True

    runtime = SemanticEscalationRuntime(BASE)
    task = {
        "role": "text_analyst",
        "complexity": 2,
        "text": "Объясни, почему в FATHER агент не равен модели и как выбирается модель.",
    }
    normal = runtime.run(task, SPEC, CONTEXT, CLAIMS, gpu_temp_c=70)
    ok &= add(rows, "normal_grounded_runtime_is_accepted",
              normal.get("ok") and
              normal.get("status") == "ACCEPTED" and
              len(normal.get("attempts", [])) >= 1 and
              (normal.get("attempts") or [{}])[0].get("semantic") is not None,
              compact(normal))

    forced = ForcedFirstRejectRuntime(BASE).run(
        task, SPEC, CONTEXT, CLAIMS, gpu_temp_c=70
    )
    ok &= add(rows, "semantic_reject_triggers_qwen7b_escalation",
              forced.get("escalated") and
              forced.get("initial_brain") == "qwen-analysis-fast" and
              forced.get("final_brain") == "qwen-analysis" and
              len(forced.get("attempts", [])) == 2,
              compact(forced))

    ok &= add(rows, "escalated_answer_is_semantically_rechecked",
              len(forced.get("attempts", [])) == 2 and
              (forced["attempts"][1].get("semantic") or {}).get("status") in {"PASS", "ESCALATE"},
              compact(forced))

    hot = runtime.run(task, SPEC, CONTEXT, CLAIMS, gpu_temp_c=91)
    ok &= add(rows, "thermal_gate_precedes_semantic_runtime",
              (not hot.get("ok")) and hot.get("status") == "EXECUTION_FAILED",
              {"ok": hot.get("ok"), "status": hot.get("status"), "reason": hot.get("reason")})

    report = {
        "benchmark": "FATHER SEMANTIC ESCALATION RUNTIME MVP-07",
        "production_path": "3B -> semantic gate -> 7B -> semantic gate",
        "fault_injection_only_for_control_flow_test": True,
        "checks": rows,
        "normal": normal,
        "forced": forced,
    }
    path = BASE / "evidence/semantic_escalation_runtime_mvp07.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("RESULT:", "PASS" if ok else "FAIL")
    print("EVIDENCE:", path)
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
