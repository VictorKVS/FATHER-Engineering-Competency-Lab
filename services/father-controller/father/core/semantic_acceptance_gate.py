import json
import re
import time
from pathlib import Path

from father.contracts.types import BrainRequest
from father.core.assembler import AgentAssembler


class SemanticAcceptanceGate:
    """Claim-anchored semantic critic for answer acceptance."""

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
        claims=[]
        for line in str(source_context).splitlines():
            item=line.strip(" -\t")
            if item:
                claims.append(item)
        return claims

    def _prompt(self, task, answer, source_context, source_claims):
        numbered="\n".join(f"C{i+1}: {c}" for i,c in enumerate(source_claims))
        return f"""Ты — FATHER Semantic Critic.

ВАЖНО:
1. REFERENCE CLAIMS ниже считаются истинными утверждениями источника.
2. Сравнивай ОТВЕТ-КАНДИДАТ с каждым reference claim.
3. Верни один claim_alignment для КАЖДОГО REFERENCE CLAIM и сохрани его claim_id.
4. Не пропускай claims: если ответ claim не затрагивает, верни NOT_ADDRESSED.
5. Если ответ повторяет смысл reference claim — relation=SUPPORTED.
6. Если ответ утверждает противоположное — relation=CONTRADICTED.
7. НЕЛЬЗЯ называть contradiction само утверждение источника.
8. Не используй внешние знания как доказательство.

ЗАДАЧА:
{task}

ИСХОДНЫЙ КОНТЕКСТ:
{source_context}

REFERENCE CLAIMS:
{numbered}

ОТВЕТ-КАНДИДАТ:
{answer}

Верни ТОЛЬКО JSON:
{{
  "claim_alignment": [
    {{"claim_id":"C1","relation":"SUPPORTED","reason":""}}
  ],
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

Оценки 0..5.
critical_error=true только если кандидат прямо противоречит ключевому reference claim
или выдумывает ключевой факт, меняющий смысл.
"""

    def evaluate(self, task, answer, source_context, threshold=None, source_claims=None):
        threshold = self.threshold if threshold is None else float(threshold)
        source_claims = list(source_claims or self._default_claims(source_context))
        req = BrainRequest(
            messages=[
                {"role": "system", "content": "Ты строгий claim-alignment контролёр. Не инвертируй направление противоречия. Вывод только JSON."},
                {"role": "user", "content": self._prompt(task, answer, source_context, source_claims)},
            ],
            temperature=0.0,
            max_tokens=900,
        )
        t0=time.perf_counter()
        response=self.brain.generate(req)
        latency_ms=round((time.perf_counter()-t0)*1000,2)

        if response.error:
            return {
                "ok":False,"accepted":False,"status":"JUDGE_ERROR",
                "reason":"judge_runtime_error","error":response.error,
                "judge_brain":response.brain_id,"judge_model":response.model,
                "latency_ms":latency_ms
            }

        try:
            data=self._extract_json(response.content)
        except Exception as e:
            return {
                "ok":False,"accepted":False,"status":"JUDGE_PARSE_ERROR",
                "reason":"judge_invalid_json","error":type(e).__name__,
                "raw":response.content[:1600],
                "judge_brain":response.brain_id,"judge_model":response.model,
                "latency_ms":latency_ms
            }

        raw_alignment=data.get("claim_alignment") or []
        by_id={}
        for item in raw_alignment:
            cid=str(item.get("claim_id","")).upper().strip()
            rel=str(item.get("relation","")).upper()
            if rel not in {"SUPPORTED","CONTRADICTED","NOT_ADDRESSED"}:
                rel="NOT_ADDRESSED"
            if cid:
                by_id[cid]={
                    "claim_id":cid,
                    "relation":rel,
                    "reason":str(item.get("reason",""))
                }

        alignment=[]
        missing_claim_ids=[]
        supported=contradicted=addressed=0
        for i,_claim in enumerate(source_claims, start=1):
            cid=f"C{i}"
            row=by_id.get(cid)
            if row is None:
                missing_claim_ids.append(cid)
                row={
                    "claim_id":cid,
                    "relation":"NOT_ADDRESSED",
                    "reason":"judge_omitted_claim"
                }
            alignment.append(row)
            if row["relation"]=="SUPPORTED":
                supported+=1
                addressed+=1
            elif row["relation"]=="CONTRADICTED":
                contradicted+=1
                addressed+=1

        claim_count=max(1,len(source_claims))
        support_ratio=round(supported/claim_count,4)
        contradiction_ratio=round(contradicted/claim_count,4)
        alignment_complete=(len(missing_claim_ids)==0)

        scores=data.get("scores") or {}
        clean={}
        for name in self.DIMENSIONS:
            try:
                value=float(scores.get(name,0))
            except Exception:
                value=0.0
            clean[name]=max(0.0,min(5.0,value))

        semantic_score=round(sum(clean.values())/(5.0*len(self.DIMENSIONS))*100.0,2)
        critical=bool(data.get("critical_error",False)) or contradicted>0

        hard_dims=(
            clean["factual_accuracy"]>=3
            and clean["source_grounding"]>=3
            and clean["task_fulfillment"]>=3
            and clean["hallucination_resistance"]>=3
        )

        accepted=bool(
            semantic_score>=threshold
            and hard_dims
            and not critical
            and support_ratio>0
            and alignment_complete
        )

        return {
            "ok":True,
            "accepted":accepted,
            "status":"PASS" if accepted else "ESCALATE",
            "semantic_score":semantic_score,
            "threshold":threshold,
            "scores":clean,
            "claim_alignment":alignment,
            "source_claims":source_claims,
            "supported_claims":supported,
            "contradicted_claims":contradicted,
            "support_ratio":support_ratio,
            "contradiction_ratio":contradiction_ratio,
            "alignment_complete":alignment_complete,
            "missing_claim_ids":missing_claim_ids,
            "unsupported_claims":data.get("unsupported_claims") or [],
            "critical_error":critical,
            "brief_reason":str(data.get("brief_reason","")),
            "judge_brain":response.brain_id,
            "judge_model":response.model,
            "latency_ms":latency_ms
        }
