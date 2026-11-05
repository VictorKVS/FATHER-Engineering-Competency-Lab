import json
from pathlib import Path

from father.core.role_model_router import RoleModelRouter


class AdaptiveRoleRouter:
    """Shadow-mode role router.

    It chooses runtime models from the evidence-backed role matrix but does not
    mutate Stage29 or ProductFactory. Promotion into production requires a
    separate acceptance step.
    """

    def __init__(self, base_dir):
        self.base=Path(base_dir)
        self.roles=RoleModelRouter(self.base)
        self.matrix=self.roles.data
        self.thermal=self.matrix.get("gates",{}).get("thermal",{})

    def classify(self, task):
        explicit=task.get("role")
        complexity=max(1,min(4,int(task.get("complexity",2))))
        text=str(task.get("text","")).lower()

        if explicit:
            role=explicit
        elif complexity<=1 and any(x in text for x in ["коротко","фразу","перефраз","перепиш","сократи","исправь"]):
            role="edge_fast"
        elif any(x in text for x in ["рассказ","сцен","диалог","продолж","стиль","творч"]) or (complexity>=2 and "перепиш" in text):
            role="creative_writing"
        elif any(x in text for x in ["код","python","api","рефактор","ошибк","функц","класс"]):
            role="coding"
        elif any(x in text for x in ["изображ","фото","скрин","диаграм","chart","vision"]):
            role="vision"
        elif any(x in text for x in ["доказ","глубок","рассуж","почему","сравни варианты","критич"]):
            role="reasoning"
        elif any(x in text for x in ["анализ","книга","текст","rag","персонаж","событ","источник"]):
            role="text_analyst"
        else:
            role="edge_fast" if complexity<=1 else "text_analyst"

        return {"role":role,"complexity":complexity}

    def _thermal_gate(self, gpu_temp_c):
        review=float(self.thermal.get("review_at_c",90))
        cooldown=float(self.thermal.get("cooldown_target_c",75))
        if gpu_temp_c is None:
            return {"ok":True,"status":"UNKNOWN","review_at_c":review,"cooldown_target_c":cooldown}
        if float(gpu_temp_c)>=review:
            return {
              "ok":False,
              "status":"THERMAL_BLOCK",
              "gpu_temp_c":float(gpu_temp_c),
              "review_at_c":review,
              "cooldown_target_c":cooldown
            }
        return {
          "ok":True,
          "status":"OK",
          "gpu_temp_c":float(gpu_temp_c),
          "review_at_c":review,
          "cooldown_target_c":cooldown
        }

    def plan(self, task, gpu_temp_c=None, allow_unbenchmarked=False, multi_draft=False):
        profile=self.classify(task)
        thermal=self._thermal_gate(gpu_temp_c)
        if not thermal["ok"]:
            return {
              "ok":False,
              "reason":"thermal_gate",
              "profile":profile,
              "thermal":thermal
            }

        role_id=profile["role"]
        decision=self.roles.choose(role_id,allow_unbenchmarked=allow_unbenchmarked)
        if not decision.get("ok"):
            return {
              "ok":False,
              "reason":decision.get("reason"),
              "profile":profile,
              "role_decision":decision,
              "thermal":thermal
            }

        candidates=list(decision.get("candidates") or [])
        selected=decision.get("preferred")
        reasons=["role_preference"]

        # Text analyst uses the economical 3B for normal work and escalates
        # difficult analysis to the 7B challenger.
        if role_id=="text_analyst":
            if profile["complexity"]>=3 and "qwen2.5:7b" in candidates:
                selected="qwen2.5:7b"
                reasons=["complexity_escalation_to_7b"]
            elif "qwen2.5:3b" in candidates:
                selected="qwen2.5:3b"
                reasons=["value_champion_for_routine_analysis"]

        # Creative lane may intentionally return several writers from one
        # shared story state for later critic/synthesis comparison.
        writers=None
        if role_id=="creative_writing" and multi_draft:
            writers=candidates[:3]
            reasons.append("multi_draft")

        return {
          "ok":True,
          "mode":"SHADOW",
          "profile":profile,
          "selected":selected,
          "candidates":candidates,
          "writers":writers,
          "reasons":reasons,
          "quality_gate":decision.get("quality_gate"),
          "thermal":thermal,
          "production_applied":False
        }
