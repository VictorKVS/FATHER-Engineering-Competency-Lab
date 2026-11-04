import json
from pathlib import Path

from father.core.auto_assembly import AutoAssemblyPlanner
from father.core.product_factory import ProductFactory

BASE=Path(__file__).resolve().parent
planner=AutoAssemblyPlanner(BASE)
factory=ProductFactory(BASE)

buildable=json.loads((BASE/"config/requirements/general_rag.json").read_text(encoding="utf-8"))
future=json.loads((BASE/"config/requirements/osint_future.json").read_text(encoding="utf-8"))

evidence={
  "milestone":"FATHER FACTORY MVP-04 / AUTO ASSEMBLY",
  "goal":"prove requirements-driven planning, REUSE/ADAPT/BUILD classification and draft Product Spec generation",
  "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== BUILDABLE REQUIREMENTS ===")
plan=planner.plan(buildable)
add("buildable_plan_ready",
    plan["ok"]
    and plan["agent_choice"]["agent_id"]=="father-general-agent"
    and plan["model_choice"]["brain_id"]=="qwen-analysis"
    and plan["product_spec"] is not None,
    plan
)

validation=factory.validate(plan["product_spec"])
add("auto_product_spec_factory_compatible",validation["ok"],validation)

built=factory.build(plan["product_spec"])
add("auto_assembled_product_ready",
    built["report"]["status"]=="ready"
    and built["report"]["brain_id"]=="qwen-analysis",
    built["report"]
)

print("\n=== REUSE / ADAPT / BUILD GAP ANALYSIS ===")
future_plan=planner.plan(future)
reuse_ids=[x["id"] for x in future_plan["gaps"]["reuse"]]
adapt_ids=[x["id"] for x in future_plan["gaps"]["adapt"]]
build_ids=[x["id"] for x in future_plan["gaps"]["build"]]

add("future_reuse_detected",
    "api" in reuse_ids and "json" in reuse_ids and "folder" in reuse_ids,
    future_plan["gaps"]
)
add("future_adapt_detected",
    "research" in adapt_ids and "evidence" in adapt_ids,
    future_plan["gaps"]
)
add("future_build_detected",
    "telegram" in build_ids and "entity-graph" in build_ids,
    future_plan["gaps"]
)
add("future_product_not_falsely_ready",
    future_plan["ok"] is False
    and future_plan["product_spec"] is None
    and any(x["id"]=="telegram" for x in future_plan["blockers"]),
    {"ok":future_plan["ok"],"blockers":future_plan["blockers"],"product_spec":future_plan["product_spec"]}
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
out=BASE/"evidence/factory_mvp04_auto_assembly.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
