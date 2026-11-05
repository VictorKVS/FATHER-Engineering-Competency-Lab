import json
import re
import time
from pathlib import Path

from father.contracts.types import BrainRequest
from father.core.assembler import AgentAssembler


class SemanticAcceptanceGate:
    """Claim-by-claim semantic critic for answer acceptance."""

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

    @staticmethod
    def _default_claims(source_context):
        claims = []
        for line in str(source_context).splitlines():
            item = line.strip(" -\t")
            if item:
                claims.append(item)
        return claims

    def _generate_json(self, prompt, max_tokens=500):
        req = BrainRequest(
            messages=[
                {"role": "system", "content": "Ты строгий контролёр FATHER. Вывод только валидный JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=max_tokens,
        )
        t0 = time.perf_counter()
        response = self.brain.generate(req)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        if response.error:
            return None, response, latency_ms, "judge_runtime_error"
        try:
            return self._extract_json(response.content), response, latency_ms, None
        except Exception:
            return None, response, latency_ms, "judge_invalid_json"

    def _judge_claim(self, task, answer, claim_id, claim):
        prompt = f"""Сравни ОТВЕТ-КАНДИДАТ только с одним истинным REFERENCE CLAIM.

ЗАДАЧА:
{task}

REFERENCE CLAIM {claim_id}:
{claim}

ОТВЕТ-КАНДИДАТ:
{answer}

Определи отношение ответа к этому claim:
- SUPPORTED: ответ подтверждает или корректно перефразирует claim;
- CONTRADICTED: ответ утверждает противоположное;
- NOT_ADDRESSED: ответ этот claim не затрагивает.

Не используй внешние знания. Не инвертируй направление сравнения.
Верни только JSON:
{{"claim_id":"{claim_id}","relation":"SUPPORTED","reason":""}}
"""
        data, response, latency_ms, error = self._generate_json(prompt, max_tokens=220)
        if error:
            return {
                "claim_id": claim_id,
                "relation": "JUDGE_ERROR",
                "reason": error,
                "latency_ms": latency_ms,
                "raw": (response.content if response else "")[:600],
            }
        relation = str(data.get("relation", "")).upper().strip()
        if relation not in {"SUPPORTED", "CONTRADICTED", "NOT_ADDRESSED"}:
            relation = "JUDGE_ERROR"
        return {
            "claim_id": claim_id,
            "relation": relation,
            "reason": str(data.get("reason", "")),
            "latency_ms": latency_ms,
        }

    def _score_answer(self, task, answer, source_context):
        prompt = f"""Оцени качество ОТВЕТА-КАНДИДАТА по задаче и данному источнику.
Не используй внешние знания как доказательство.

ЗАДАЧА:
{task}

ИСТОЧНИК:
{source_context}

ОТВЕТ-КАНДИДАТ:
{answer}

Верни только JSON:
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
  "critical_error": false,
  "brief_reason": ""
}}
Каждая оценка 0..5.
"""
        return self._generate_json(prompt, max_tokens=650)

    def evaluate(self, task, answer, source_context, threshold=None, source_claims=None):
        threshold = self.threshold if threshold is None else float(threshold)
        source_claims = list(source_claims or self._default_claims(source_context))

        alignment = []
        claim_latency_ms = 0.0
        judge_errors = []
        for i, claim in enumerate(source_claims, start=1):
            row = self._judge_claim(task, answer, f"C{i}", claim)
            alignment.append(row)
            claim_latency_ms += float(row.get("latency_ms") or 0.0)
            if row.get("relation") == "JUDGE_ERROR":
                judge_errors.append(row.get("claim_id"))

        score_data, score_response, score_latency_ms, score_error = self._score_answer(
            task, answer, source_context
        )
        total_latency_ms = round(claim_latency_ms + score_latency_ms, 2)

        if score_error:
            return {
                "ok": False,
                "accepted": False,
                "status": "JUDGE_ERROR",
                "reason": score_error,
                "claim_alignment": alignment,
                "judge_error_claim_ids": judge_errors,
                "judge_brain": score_response.brain_id if score_response else self.judge_brain_id,
                "judge_model": score_response.model if score_response else None,
                "latency_ms": total_latency_ms,
            }

        supported = sum(1 for x in alignment if x.get("relation") == "SUPPORTED")
        contradicted = sum(1 for x in alignment if x.get("relation") == "CONTRADICTED")
        not_addressed = sum(1 for x in alignment if x.get("relation") == "NOT_ADDRESSED")
        claim_count = max(1, len(source_claims))
        support_ratio = round(supported / claim_count, 4)
        contradiction_ratio = round(contradicted / claim_count, 4)
        alignment_complete = (len(alignment) == len(source_claims) and not judge_errors)

        scores = (score_data or {}).get("scores") or {}
        clean = {}
        for name in self.DIMENSIONS:
            try:
                value = float(scores.get(name, 0))
            except Exception:
                value = 0.0
            clean[name] = max(0.0, min(5.0, value))

        semantic_score = round(sum(clean.values()) / (5.0 * len(self.DIMENSIONS)) * 100.0, 2)
        critical = bool((score_data or {}).get("critical_error", False)) or contradicted > 0
        hard_dims = (
            clean["factual_accuracy"] >= 3
            and clean["source_grounding"] >= 3
            and clean["task_fulfillment"] >= 3
            and clean["hallucination_resistance"] >= 3
        )
        accepted = bool(
            semantic_score >= threshold
            and hard_dims
            and not critical
            and support_ratio > 0
            and alignment_complete
        )

        return {
            "ok": True,
            "accepted": accepted,
            "status": "PASS" if accepted else "ESCALATE",
            "semantic_score": semantic_score,
            "threshold": threshold,
            "scores": clean,
            "claim_alignment": alignment,
            "source_claims": source_claims,
            "supported_claims": supported,
            "contradicted_claims": contradicted,
            "not_addressed_claims": not_addressed,
            "support_ratio": support_ratio,
            "contradiction_ratio": contradiction_ratio,
            "alignment_complete": alignment_complete,
            "missing_claim_ids": [],
            "judge_error_claim_ids": judge_errors,
            "unsupported_claims": (score_data or {}).get("unsupported_claims") or [],
            "critical_error": critical,
            "brief_reason": str((score_data or {}).get("brief_reason", "")),
            "judge_brain": score_response.brain_id,
            "judge_model": score_response.model,
            "latency_ms": total_latency_ms,
        }
