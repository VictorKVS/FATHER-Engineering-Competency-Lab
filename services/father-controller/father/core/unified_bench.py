import json
import time
from copy import deepcopy
from pathlib import Path

from father.core.product_factory import ProductFactory, FactoryBuildError
from father.core.io import ApiInputAdapter

class UnifiedBench:
    def __init__(self,base_dir):
        self.base=Path(base_dir)
        self.factory=ProductFactory(self.base)
        self.api=ApiInputAdapter()

    def run(self,spec,smoke_text="Объясни кратко назначение FATHER Agent Chassis."):
        checks=[]
        started=time.time()

        def add(name,passed,details):
            checks.append({"name":name,"passed":bool(passed),"details":details})

        validation=self.factory.validate(spec)
        add("product_spec_valid",validation["ok"],validation)

        product=None
        if validation["ok"]:
            try:
                product=self.factory.build(spec)
                add("product_build_ready",
                    product["report"]["status"]=="ready",
                    product["report"]
                )
            except Exception as e:
                add("product_build_ready",False,{"error":str(e)})
        else:
            add("product_build_ready",False,{"reason":"validation_failed"})

        execution=None
        if product:
            try:
                event=self.api.normalize({
                    "type":"bench-smoke",
                    "content":smoke_text,
                    "metadata":{"bench":"mvp05"}
                })
                t0=time.time()
                execution=product["runtime"].run(event,"bench")
                latency_ms=round((time.time()-t0)*1000,2)
                add("runtime_executes",
                    execution.get("ok") is True,
                    {
                        "ok":execution.get("ok"),
                        "brain_id":execution.get("brain_id"),
                        "latency_ms":latency_ms
                    }
                )
                add("nonempty_output",
                    bool((execution.get("content") or "").strip()),
                    {"content_chars":len(execution.get("content") or "")}
                )
                add("knowledge_path_operational",
                    execution.get("knowledge_hits",0)>=1,
                    {
                        "knowledge_hits":execution.get("knowledge_hits"),
                        "knowledge_sources":execution.get("knowledge_sources"),
                        "knowledge_modes":execution.get("knowledge_modes")
                    }
                )
                add("brain_matches_spec",
                    execution.get("brain_id")==spec.get("brain_id"),
                    {
                        "expected":spec.get("brain_id"),
                        "actual":execution.get("brain_id")
                    }
                )
            except Exception as e:
                add("runtime_executes",False,{"error":str(e)})
                add("nonempty_output",False,{"reason":"runtime_failed"})
                add("knowledge_path_operational",False,{"reason":"runtime_failed"})
                add("brain_matches_spec",False,{"reason":"runtime_failed"})

        # deterministic I/O checks without invoking extra model calls
        if product:
            expected_inputs=sorted(spec.get("inputs",[]))
            expected_outputs=sorted(spec.get("outputs",[]))
            add("io_contract_matches",
                sorted(product["inputs"])==expected_inputs
                and sorted(product["outputs"])==expected_outputs,
                {
                    "expected_inputs":expected_inputs,
                    "actual_inputs":sorted(product["inputs"]),
                    "expected_outputs":expected_outputs,
                    "actual_outputs":sorted(product["outputs"])
                }
            )

            tools=[x["name"] for x in product["agent"].tools.list()]
            add("tool_profile_loaded",
                len(tools)>=1,
                {"tools":tools}
            )

        passed=all(x["passed"] for x in checks)
        return {
            "product_id":spec.get("product_id"),
            "status":"READY" if passed else "BLOCKED",
            "checks":checks,
            "summary":{
                "passed":sum(1 for x in checks if x["passed"]),
                "failed":sum(1 for x in checks if not x["passed"]),
                "total":len(checks),
                "duration_ms":round((time.time()-started)*1000,2)
            },
            "execution":execution
        }

    def acceptance(self,spec,**kwargs):
        return self.run(spec,**kwargs)
