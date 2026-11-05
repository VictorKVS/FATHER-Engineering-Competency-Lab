import time
from copy import deepcopy
from pathlib import Path

from father.core.hybrid_runtime_router import HybridRuntimeRouter


class EscalatingRuntime:
    """MVP-05 execution telemetry + deterministic escalation.

    Semantic quality judging is intentionally outside this MVP. The gate uses
    runtime-verifiable acceptance criteria only.
    """

    def __init__(self, base_dir):
        self.base=Path(base_dir)
        self.router=HybridRuntimeRouter(self.base)

    @staticmethod
    def evaluate(result, acceptance=None):
        acceptance=acceptance or {}
        reasons=[]

        if not result.get("ok"):
            reasons.append("runtime_error")

        content=str(result.get("content") or "")
        min_chars=int(acceptance.get("min_chars",1))
        if len(content)<min_chars:
            reasons.append(f"content_too_short:{len(content)}<{min_chars}")

        for term in acceptance.get("required_terms",[]) or []:
            if str(term).lower() not in content.lower():
                reasons.append("missing_required_term:"+str(term))

        return {
            "accepted":not reasons,
            "reasons":reasons,
            "content_chars":len(content)
        }

    def _execute(self, task, spec, gpu_temp_c=None):
        built=self.router.build(task,spec,gpu_temp_c=gpu_temp_c)
        if not built.get("ok"):
            return {"ok":False,"build":built}

        product=built["product"]
        event=product["inputs"]["api"].normalize({
          "type":"message",
          "content":task.get("text",""),
          "metadata":{"runtime":"escalating-mvp05"}
        })
        t0=time.perf_counter()
        result=product["runtime"].run(event)
        elapsed=round((time.perf_counter()-t0)*1000,2)
        return {
          "ok":True,
          "plan":built["plan"],
          "result":result,
          "telemetry":{
            "brain_id":result.get("brain_id"),
            "runtime_model":built["plan"].get("runtime_model"),
            "latency_ms":elapsed,
            "content_chars":len(result.get("content") or ""),
            "error":result.get("error"),
            "source":built["plan"].get("source"),
            "fallback_used":built["plan"].get("fallback_used")
          }
        }

    def run(self, task, product_spec, gpu_temp_c=None, acceptance=None):
        first=self._execute(task,product_spec,gpu_temp_c=gpu_temp_c)
        if not first.get("ok"):
            return {
              "ok":False,
              "reason":"initial_execution_failed",
              "attempts":[first]
            }

        first_gate=self.evaluate(first["result"],acceptance)
        attempts=[{**first["telemetry"],"acceptance":first_gate}]

        if first_gate["accepted"]:
            return {
              "ok":True,
              "escalated":False,
              "final_brain":first["result"].get("brain_id"),
              "final_result":first["result"],
              "attempts":attempts,
              "escalation_reason":[]
            }

        role=(first["plan"].get("role") or
              (first["plan"].get("role_plan") or {}).get("profile",{}).get("role"))

        # Only the already-proven TEXT_ANALYST 3B -> 7B path is promoted here.
        if role!="text_analyst" or first["result"].get("brain_id")!="qwen-analysis-fast":
            return {
              "ok":False,
              "reason":"no_approved_escalation_path",
              "escalated":False,
              "attempts":attempts,
              "escalation_reason":first_gate["reasons"]
            }

        escalated_task=deepcopy(task)
        escalated_task["role"]="text_analyst"
        escalated_task["complexity"]=max(3,int(task.get("complexity",2)))
        second=self._execute(escalated_task,product_spec,gpu_temp_c=gpu_temp_c)
        if not second.get("ok"):
            return {
              "ok":False,
              "reason":"escalated_execution_failed",
              "escalated":True,
              "attempts":attempts+[second],
              "escalation_reason":first_gate["reasons"]
            }

        second_gate=self.evaluate(second["result"],acceptance)
        attempts.append({**second["telemetry"],"acceptance":second_gate})

        return {
          "ok":bool(second["result"].get("ok",False) and second_gate["accepted"]),
          "reason":None if second_gate["accepted"] else "final_acceptance_failed",
          "status":"ACCEPTED" if second_gate["accepted"] else "ESCALATION_EXHAUSTED",
          "escalated":True,
          "initial_brain":first["result"].get("brain_id"),
          "final_brain":second["result"].get("brain_id"),
          "final_result":second["result"],
          "attempts":attempts,
          "escalation_reason":first_gate["reasons"],
          "final_acceptance":second_gate
        }
