import json
from copy import deepcopy
from pathlib import Path

from father.core.auto_assembly import AutoAssemblyPlanner
from father.core.unified_bench import UnifiedBench

BASE=Path(__file__).resolve().parent
planner=AutoAssemblyPlanner(BASE)
bench=UnifiedBench(BASE)

req=json.loads((BASE/"config/requirements/general_rag.json").read_text(encoding="utf-8"))
plan=planner.plan(req)

evidence={
  "milestone":"FATHER FACTORY MVP-05 / UNIFIED BENCH",
  "goal":"prove one acceptance gate can classify assembled products as READY or BLOCKED",
  "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== READY PRODUCT ===")
ready=bench.acceptance(plan["product_spec"])
add("ready_product_accepted",
    ready["status"]=="READY"
    and ready["summary"]["failed"]==0
    and ready["summary"]["total"]>=8,
    {
      "status":ready["status"],
      "summary":ready["summary"],
      "checks":ready["checks"]
    }
)

print("\n=== BLOCKED PRODUCT ===")
bad=deepcopy(plan["product_spec"])
bad["brain_id"]="missing-bench-brain"
blocked=bench.acceptance(bad)
add("invalid_product_blocked",
    blocked["status"]=="BLOCKED"
    and blocked["summary"]["failed"]>=1
    and any(x["name"]=="product_spec_valid" and not x["passed"] for x in blocked["checks"]),
    {
      "status":blocked["status"],
      "summary":blocked["summary"],
      "checks":blocked["checks"]
    }
)

print("\n=== ACCEPTANCE CONTRACT ===")
profile=json.loads((BASE/"config/bench_profiles/default_acceptance.json").read_text(encoding="utf-8"))
required=set(profile["required_checks"])
seen={x["name"] for x in ready["checks"]}
add("required_acceptance_checks_present",
    required.issubset(seen),
    {"required":sorted(required),"seen":sorted(seen)}
)

release=all(x["passed"] for x in evidence["checks"])
evidence["ready_result"]=ready
evidence["blocked_result"]=blocked
evidence["result"]="PASS" if release else "FAIL"
out=BASE/"evidence/factory_mvp05_unified_bench.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
