import json
from pathlib import Path

from father.core.semantic_acceptance_gate import SemanticAcceptanceGate

BASE = Path(__file__).resolve().parent

CONTEXT = """FATHER — инженерная фабрика AI-систем.
Агент и модель разделены: модель является заменяемым Brain-слотом агента.
Один агент может работать с разными совместимыми моделями.
Модель выбирается по роли, качеству, скорости, экономике и ограничениям.
Ни один компонент не считается готовым, пока его работа не доказана в составе конечного изделия."""

TASK = "Объясни принцип FATHER: почему агент не равен модели и зачем модель сделана заменяемой?"

GOOD = """В FATHER агент не равен модели. Агент задаёт роль и конструкцию системы, а LLM подключается как заменяемый Brain-слот. Поэтому совместимую модель можно менять под задачу и выбирать по качеству, скорости, экономике и ограничениям, не создавая заново весь агент."""

BAD = """В FATHER агент и модель — одно и то же. После создания агента модель навсегда вшивается в него и заменять её нельзя. Это нужно, чтобы всегда использовать только одну самую мощную модель независимо от стоимости и задачи."""

def add(rows, name, passed, details):
    rows.append({"name": name, "passed": bool(passed), "details": details})
    print(("PASS" if passed else "FAIL"), name, json.dumps(details, ensure_ascii=False))
    return bool(passed)

def compact(x):
    return {
        "ok": x.get("ok"),
        "accepted": x.get("accepted"),
        "status": x.get("status"),
        "semantic_score": x.get("semantic_score"),
        "grounded_semantic_score": x.get("grounded_semantic_score"),
        "judge_quality_score": x.get("judge_quality_score"),
        "critical_error": x.get("critical_error"),
        "scores": x.get("scores"),
        "claim_alignment": x.get("claim_alignment"),
        "supported_claims": x.get("supported_claims"),
        "contradicted_claims": x.get("contradicted_claims"),
        "support_ratio": x.get("support_ratio"),
        "alignment_complete": x.get("alignment_complete"),
        "missing_claim_ids": x.get("missing_claim_ids"),
        "unsupported_claims": x.get("unsupported_claims"),
        "brief_reason": x.get("brief_reason"),
        "judge_brain": x.get("judge_brain"),
        "judge_model": x.get("judge_model"),
        "latency_ms": x.get("latency_ms"),
    }

def main():
    gate = SemanticAcceptanceGate(BASE, judge_brain_id="qwen-analysis", threshold=70)
    rows = []
    ok = True

    claims = [
        "Агент и модель разделены: модель является заменяемым Brain-слотом агента.",
        "Один агент может работать с разными совместимыми моделями.",
        "Модель выбирается по роли, качеству, скорости, экономике и ограничениям.",
    ]

    good = gate.evaluate(TASK, GOOD, CONTEXT, source_claims=claims)
    ok &= add(rows, "grounded_answer_passes_semantic_gate",
              good.get("ok") and good.get("accepted") and good.get("status") == "PASS",
              compact(good))

    bad = gate.evaluate(TASK, BAD, CONTEXT, source_claims=claims)
    ok &= add(rows, "contradictory_answer_is_rejected",
              bad.get("ok") and (not bad.get("accepted")) and bad.get("status") == "ESCALATE",
              compact(bad))

    ok &= add(rows, "good_answer_has_no_source_contradiction",
              good.get("alignment_complete") and good.get("contradicted_claims") == 0 and good.get("supported_claims", 0) >= 2,
              {"supported": good.get("supported_claims"), "contradicted": good.get("contradicted_claims"), "alignment": good.get("claim_alignment")})

    ok &= add(rows, "claim_alignment_is_complete",
              good.get("alignment_complete") and bad.get("alignment_complete"),
              {"good_missing": good.get("missing_claim_ids"), "bad_missing": bad.get("missing_claim_ids")})

    ok &= add(rows, "bad_answer_has_source_contradiction",
              bad.get("contradicted_claims", 0) >= 1,
              {"supported": bad.get("supported_claims"), "contradicted": bad.get("contradicted_claims"), "alignment": bad.get("claim_alignment")})

    ok &= add(rows, "semantic_gate_distinguishes_quality",
              good.get("grounded_semantic_score", 0) > bad.get("grounded_semantic_score", 100),
              {"good_grounded": good.get("grounded_semantic_score"), "bad_grounded": bad.get("grounded_semantic_score"), "good_judge_quality": good.get("judge_quality_score"), "bad_judge_quality": bad.get("judge_quality_score")})

    ok &= add(rows, "judge_is_separate_brain",
              good.get("judge_brain") == "qwen-analysis" and good.get("judge_model") == "qwen2.5:7b",
              {"judge_brain": good.get("judge_brain"), "judge_model": good.get("judge_model")})

    report = {
        "benchmark": "FATHER SEMANTIC ACCEPTANCE GATE / CRITIC MVP-06",
        "judge": "qwen-analysis / qwen2.5:7b",
        "threshold": 70,
        "checks": rows,
        "good": good,
        "bad": bad,
    }
    path = BASE / "evidence/semantic_acceptance_gate_mvp06.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("RESULT:", "PASS" if ok else "FAIL")
    print("EVIDENCE:", path)
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
