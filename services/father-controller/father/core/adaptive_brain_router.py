import json
from copy import deepcopy
from pathlib import Path

from father.core.model_applicability import ModelApplicabilityEngine
from father.core.product_factory import ProductFactory, FactoryBuildError

class AdaptiveBrainRouter:
    def __init__(self,base_dir):
        self.base=Path(base_dir)
        self.engine=ModelApplicabilityEngine(self.base/"config/model_knowledge_base.json")
        self.factory=ProductFactory(self.base)

    def plan(self,task,product_spec):
        decision=self.engine.choose(task,registered_only=True)
        selected=decision.get("selected")
        if not selected or not selected.get("brain_id"):
            return {
                "ok":False,
                "reason":"no_compatible_registered_brain",
                "task_profile":decision.get("task_profile"),
                "ranking":decision.get("ranking",[])
            }

        spec=deepcopy(product_spec)
        spec["brain_id"]=selected["brain_id"]

        validation=self.factory.validate(spec)
        if not validation["ok"]:
            return {
                "ok":False,
                "reason":"selected_product_incompatible",
                "task_profile":decision.get("task_profile"),
                "selected":selected,
                "validation":validation,
                "ranking":decision.get("ranking",[])
            }

        return {
            "ok":True,
            "task_profile":decision["task_profile"],
            "selected":selected,
            "product_spec":spec,
            "validation":validation,
            "ranking":decision["ranking"]
        }

    def build(self,task,product_spec):
        plan=self.plan(task,product_spec)
        if not plan["ok"]:
            raise FactoryBuildError(json.dumps(plan,ensure_ascii=False))
        product=self.factory.build(plan["product_spec"])
        return {
            "plan":plan,
            "product":product
        }
