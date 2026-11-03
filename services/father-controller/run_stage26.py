import json
from pathlib import Path

from father.core.product_factory import ProductFactory, FactoryBuildError

BASE=Path(__file__).resolve().parent
factory=ProductFactory(BASE)

evidence={
    "stage":"FATHER Product Factory v1 / Stage 26",
    "goal":"prove config-driven assembly of multiple agent products from one chassis",
    "checks":[],
    "products":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== BUILD GENERAL SINGLE-BRAIN PRODUCT ===")
spec1=factory.load_spec("config/products/father_general_single.json")
build1=factory.build(spec1)
evidence["products"].append(build1["report"])
add("general_product_ready",
    build1["report"]["status"]=="ready"
    and build1["report"]["brain_id"]=="qwen-analysis"
    and build1["report"]["knowledge"]["adapter"]=="folder",
    build1["report"]
)

event1=build1["inputs"]["api"].normalize({
    "type":"architecture",
    "content":"Что такое Brain Slot в FATHER?",
    "metadata":{"stage":26}
})
result1=build1["runtime"].run(event1,"architecture")
json1=build1["outputs"]["json"].emit(result1)
add("general_product_executes",
    result1["ok"] and result1["knowledge_hits"]>0 and '"content"' in json1,
    {
        "ok":result1["ok"],
        "brain_id":result1["brain_id"],
        "knowledge_hits":result1["knowledge_hits"],
        "inputs":build1["report"]["inputs"],
        "outputs":build1["report"]["outputs"]
    }
)

print("\n=== BUILD CODER PRODUCT FROM SAME CHASSIS ===")
spec2=factory.load_spec("config/products/father_coder_single.json")
build2=factory.build(spec2)
evidence["products"].append(build2["report"])
add("coder_product_ready",
    build2["report"]["status"]=="ready"
    and build2["report"]["brain_id"]=="qwen-coder"
    and build2["report"]["agent_id"]=="father-coder-agent",
    build2["report"]
)

add("same_chassis_different_product",
    build1["report"]["brain_id"]!=build2["report"]["brain_id"]
    and build1["report"]["agent_id"]!=build2["report"]["agent_id"]
    and build1["report"]["inputs"]==build2["report"]["inputs"]
    and build1["report"]["outputs"]==build2["report"]["outputs"],
    {
        "product_1":build1["report"],
        "product_2":build2["report"]
    }
)

print("\n=== PRODUCT SPEC VALIDATION ===")
bad=dict(spec1)
bad["brain_id"]="missing-stage26-brain"
validation=factory.validate(bad)
add("invalid_product_blocked",
    validation["ok"] is False
    and any(x.get("kind")=="unknown_brain" for x in validation["problems"]),
    validation
)

print("\n=== INPUT / OUTPUT ADAPTER ASSEMBLY ===")
add("io_adapters_assembled",
    sorted(build1["inputs"])==["api","file"]
    and sorted(build1["outputs"])==["file","json"],
    {
        "inputs":sorted(build1["inputs"]),
        "outputs":sorted(build1["outputs"])
    }
)

print("\n=== SLOT MAP ===")
slot_map={
    "brain":build1["report"]["brain_id"],
    "prompt_loaded":build1["report"]["prompt_loaded"],
    "knowledge":build1["report"]["knowledge"]["adapter"],
    "tools":build1["report"]["tools"],
    "inputs":build1["report"]["inputs"],
    "outputs":build1["report"]["outputs"],
    "context_bus":build1["report"]["context_bus"]
}
add("product_slot_map_complete",
    bool(slot_map["brain"])
    and slot_map["prompt_loaded"]
    and bool(slot_map["knowledge"])
    and bool(slot_map["tools"])
    and bool(slot_map["inputs"])
    and bool(slot_map["outputs"])
    and slot_map["context_bus"],
    slot_map
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage26_product_factory.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
