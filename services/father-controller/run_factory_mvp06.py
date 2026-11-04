import json
import shutil
from copy import deepcopy
from pathlib import Path

from father.core.auto_assembly import AutoAssemblyPlanner
from father.core.unified_bench import UnifiedBench
from father.core.release_line import PrimitiveReleaseLine

BASE=Path(__file__).resolve().parent
planner=AutoAssemblyPlanner(BASE)
bench=UnifiedBench(BASE)
release_line=PrimitiveReleaseLine(BASE)

req=json.loads((BASE/"config/requirements/general_rag.json").read_text(encoding="utf-8"))
plan=planner.plan(req)
spec=plan["product_spec"]
bench_result=bench.acceptance(spec)

evidence={
  "milestone":"FATHER FACTORY MVP-06 / PRIMITIVE RELEASE LINE",
  "goal":"prove only READY products receive a verifiable release package",
  "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

release_id="father-auto-general-rag-v1-mvp06"
target=BASE/"releases"/release_id
if target.exists():
    shutil.rmtree(target)

print("=== READY RELEASE ===")
released=release_line.release(
    spec,
    bench_result,
    build_report={
        "product_id":spec["product_id"],
        "agent_manifest":spec["agent_manifest"],
        "brain_id":spec["brain_id"],
        "status":"ready"
    },
    model_selection={
        "selected":plan.get("model_choice"),
        "ranking":plan.get("model_ranking",[])
    },
    release_id=release_id
)
add("ready_product_released",
    released["released"] is True
    and released["status"]=="READY"
    and target.exists(),
    released
)

expected_files={
    "product_spec.json",
    "bench_report.json",
    "build_report.json",
    "model_selection.json",
    "release_manifest.json",
    "READY.json"
}
actual_files={x.name for x in target.iterdir()} if target.exists() else set()
add("release_package_complete",
    expected_files.issubset(actual_files),
    {"expected":sorted(expected_files),"actual":sorted(actual_files)}
)

verification=release_line.verify(release_id)
add("release_verifies",
    verification["ok"] is True,
    verification
)

print("\n=== BLOCKED PRODUCT CONTROL ===")
bad_spec=deepcopy(spec)
bad_spec["brain_id"]="missing-release-brain"
blocked_bench=bench.acceptance(bad_spec)
blocked_id="father-blocked-mvp06"
blocked_target=BASE/"releases"/blocked_id
if blocked_target.exists():
    shutil.rmtree(blocked_target)
blocked_release=release_line.release(
    bad_spec,
    blocked_bench,
    release_id=blocked_id
)
add("blocked_product_not_released",
    blocked_release["released"] is False
    and blocked_release["status"]=="BLOCKED"
    and not blocked_target.exists(),
    blocked_release
)

print("\n=== TAMPER DETECTION ===")
spec_path=target/"product_spec.json"
original=spec_path.read_text(encoding="utf-8")
spec_path.write_text(original+"\n ",encoding="utf-8")
tampered=release_line.verify(release_id)
add("release_tamper_detected",
    tampered["ok"] is False
    and any(x.get("kind")=="artifact_hash_mismatch" for x in tampered["problems"]),
    tampered
)
spec_path.write_text(original,encoding="utf-8")
restored=release_line.verify(release_id)
add("release_restored_verifies",
    restored["ok"] is True,
    restored
)

release=all(x["passed"] for x in evidence["checks"])
evidence["release"]=released
evidence["verification"]=restored
evidence["result"]="PASS" if release else "FAIL"
out=BASE/"evidence/factory_mvp06_release_line.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("RELEASE:",target)
raise SystemExit(0 if release else 1)
