import json
import re
import time
from pathlib import Path

from father.contracts.types import BrainRequest
from father.core.assembler import AgentAssembler


class SemanticAcceptanceGate:
    """LLM semantic critic for answer acceptance."""

    DIMENSIONS = [
        "factual_accuracy",
        "source_grounding",
        "task_fulfillment",
        "completeness",
        "uncertainty_handling",
        "hallucination_resistance",
        "internal_consistency",
    ]

    def __init__(self, base_dir, judge_brain_id="qwen-analysis", threshold=70.0):
        self.base = Path(base_dir)
        self.judge_brain_id = judge_brain_id
        self.threshold = float(threshold)
        self.brain = AgentAssembler(self.base).brain(judge_brain_id)

    @staticmethod
    def _extract_json(text):
        raw = (text or "").strip()
        try:
            return json.loads(raw)
        except Exception:
            m = re.search(r"\{.*\}", raw, re.S)
            if not m:
                raise
            return json.loads(m.group(0))

    def _prompt(self, task, answer, source_context):
        return f"""Ты — FATHER Semantic Critic. Оцени ответ СТРОГО по задаче и предоставленному контексту.
Не используй внешние знания как доказательство. Если контекст не подтверждает утверждение, считай его неподтвержденным.

ЗАДАЧА:
{task}

КОНТЕКСТ / ИСТОЧНИКИ:
{source_context}

ОТВЕТ-КАНДИДАТ:
{answer}

Верни ТОЛЬКО JSON без markdown:
{{
  "scores": {{
    "factual_accuracy": 0,
    "source_grounding": 0,
    "task_fulfillment": 0,
    "completeness": 0,
    "uncertainty_handling": 0,
    "hallucination_resistance": 0,
    "internal_consistency": 0
  }},
  "unsupported_claims": [],
  "contradictions": [],
  "critical_error": false,
  "brief_reason": ""
}}

Каждая оценка — целое число 0..5.
5 = полностью выполнено; 0 = критически плохо.
critical_error=true при прямом противоречии ключевому факту источника или грубой выдумке, меняющей смысл.
"""

    def evaluate(self, task, answer, source_context, threshold=None):
        threshold = self.threshold if threshold is None else float(threshold)
        req = BrainRequest(
            messages=[
                {"role": "system", "content": "Ты строгий контролёр качества FATHER. Вывод только валидный JSON."},
                {"role": "user", "content": self._prompt(task, answer, source_context)},
            ],
            temperature=0.0,
            max_tokens=700,
        )
        t0 = time.perf_counter()
        response = self.brain.generate(req)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        if response.error:
            return {
                "ok": False, "accepted": False, "status": "JUDGE_ERROR",
                "reason": "judge_runtime_error", "error": response.error,
                "judge_brain": response.brain_id, "judge_model": response.model,
                "latency_ms": latency_ms,
            }

        try:
            data = self._extract_json(response.content)
        except Exception as e:
            return {
                "ok": False, "accepted": False, "status": "JUDGE_PARSE_ERROR",
                "reason": "judge_invalid_json", "error": type(e).__name__,
                "raw": response.content[:1200],
                "judge_brain": response.brain_id, "judge_model": response.model,
                "latency_ms": latency_ms,
            }

        scores = data.get("scores") or {}
        clean = {}
        for name in self.DIMENSIONS:
            try:
                value = float(scores.get(name, 0))
            except Exception:
                value = 0.0
            clean[name] = max(0.0, min(5.0, value))

        semantic_score = round(sum(clean.values()) / (5.0 * len(self.DIMENSIONS)) * 100.0, 2)
        critical = bool(data.get("critical_error", False))
        hard_dims = (
            clean["factual_accuracy"] >= 3
            and clean["source_grounding"] >= 3
            and clean["task_fulfillment"] >= 3
            and clean["hallucination_resistance"] >= 3
        )
        accepted = bool(semantic_score >= threshold and hard_dims and not critical)

        return {
            "ok": True,
            "accepted": accepted,
            "status": "PASS" if accepted else "ESCALATE",
            "semantic_score": semantic_score,
            "threshold": threshold,
            "scores": clean,
            "unsupported_claims": data.get("unsupported_claims") or [],
            "contradictions": data.get("contradictions") or [],
            "critical_error": critical,
            "brief_reason": str(data.get("brief_reason", "")),
            "judge_brain": response.brain_id,
            "judge_model": response.model,
            "latency_ms": latency_ms,
        }
