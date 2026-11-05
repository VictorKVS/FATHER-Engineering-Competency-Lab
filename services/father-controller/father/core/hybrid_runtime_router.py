import json
from copy import deepcopy
from pathlib import Path

from father.core.adaptive_brain_router import AdaptiveBrainRouter
from father.core.adaptive_role_router import AdaptiveRoleRouter
from father.core.product_factory import ProductFactory


RUNTIME_TO_BRAIN={
    "qwen2.5:3b":"qwen-analysis-fast",
    "qwen2.5:7b":"qwen-analysis",
    "llama3.2:1b":"llama-small",
    "qwen2.5-coder:7b-instruct-q4_K_M":"qwen-coder",
    "deepseek-r1:7b":"deepseek-reasoning",
}


class HybridRuntimeRouter:
    """MVP-03 runtime integration.

    New role router is primary only for accepted role lanes.
    Stage29 remains fallback for roles that are not yet promoted.
    """

    PROMOTED_ROLES={"text_analyst","edge_fast"}

    def __init__(self, base_dir):
        self.base=Path(base_dir)
        self.role_router=AdaptiveRoleRouter(self.base)
        self.legacy=AdaptiveBrainRouter(self.base)
        self.factory=ProductFactory(self.base)

    def plan(self, task, product_spec, gpu_temp_c=None):
        role_plan=self.role_router.plan(task,gpu_temp_c=gpu_temp_c)

        # Thermal safety is never bypassed by fallback.
        if not role_plan.get("ok") and role_plan.get("reason")=="thermal_gate":
            return {
                "ok":False,
                "reason":"thermal_gate",
                "source":"role_router",
                "role_plan":role_plan
            }

        role_id=(role_plan.get("profile") or {}).get("role")
        if role_plan.get("ok") and role_id in self.PROMOTED_ROLES:
            runtime_model=role_plan.get("selected")
            brain_id=RUNTIME_TO_BRAIN.get(runtime_model)
            if brain_id:
                spec=deepcopy(product_spec)
                spec["brain_id"]=brain_id
                validation=self.factory.validate(spec)
                if validation["ok"]:
                    return {
                        "ok":True,
                        "source":"role_router",
                        "role":role_id,
                        "runtime_model":runtime_model,
                        "brain_id":brain_id,
                        "product_spec":spec,
                        "validation":validation,
                        "fallback_used":False,
                        "role_plan":role_plan
                    }

        # Controlled fallback: existing Stage29 logic stays authoritative
        # for all not-yet-promoted roles or incompatible role selections.
        legacy=self.legacy.plan(task,product_spec)
        if not legacy.get("ok"):
            return {
                "ok":False,
                "reason":"both_routers_failed",
                "source":"fallback",
                "role_plan":role_plan,
                "legacy_plan":legacy
            }

        return {
            "ok":True,
            "source":"stage29_fallback",
            "role":role_id,
            "runtime_model":legacy["selected"].get("runtime_model"),
            "brain_id":legacy["selected"].get("brain_id"),
            "product_spec":legacy["product_spec"],
            "validation":legacy["validation"],
            "fallback_used":True,
            "role_plan":role_plan,
            "legacy_plan":legacy
        }

    def build(self, task, product_spec, gpu_temp_c=None):
        plan=self.plan(task,product_spec,gpu_temp_c=gpu_temp_c)
        if not plan.get("ok"):
            return {"ok":False,"plan":plan,"product":None}
        product=self.factory.build(plan["product_spec"])
        return {"ok":True,"plan":plan,"product":product}
