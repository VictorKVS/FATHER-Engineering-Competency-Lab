import json
from pathlib import Path

from father.core.block_registry import BlockRegistry
from father.core.product_factory import ProductFactory, FactoryBuildError

BASE=Path(__file__).resolve().parent
registry=BlockRegistry(BASE/"config/blocks.json")
factory=ProductFactory(BASE)

evidence={
    "stage":"FATHER Block Registry v1 / Stage 27",
    "goal":"prove registry-driven product assembly and compatibility checks",
    "checks":[],
    "catalog":{}
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== REGISTRY HEALTH ===")
health=registry.health()
evidence["catalog"]["health"]=health
add("registry_health",health["status"]=="ok" and health["blocks"]>=14,health)

for block_type in ["brain","competency","knowledge","input","output","tool_profile"]:
    rows=registry.list(block_type)
    evidence["catalog"][block_type]=rows
    add("registry_type_"+block_type,len(rows)>0,{"type":block_type,"count":len(rows),"items":[x["id"] for x in rows]})

print("\n=== FACTORY USES REGISTRY ===")
spec=factory.load_spec("config/products/father_general_single.json")
compat=registry.compatible(spec)
add("general_spec_registry_compatible",compat["ok"],compat)

build=factory.build(spec)
add("registry_driven_build_ready",
    build["report"]["status"]=="ready"
    and build["report"]["registry"]["status"]=="ok",
    build["report"]
)

print("\n=== HYBRID PRODUCT REGISTRY CHECK ===")
hybrid=factory.load_spec("config/products/father_general_hybrid.json")
hybrid_check=registry.compatible(hybrid)
add("hybrid_spec_registry_compatible",
    hybrid_check["ok"],
    hybrid_check
)

print("\n=== NEGATIVE CONTROL: UNKNOWN INPUT BLOCK ===")
bad_input=json.loads(json.dumps(spec))
bad_input["inputs"].append("mqtt-stage27-missing")
bad_input_check=factory.validate(bad_input)
add("registry_blocks_unknown_input",
    bad_input_check["ok"] is False
    and any(x.get("kind") in ("unsupported_input","registry_missing_input") for x in bad_input_check["problems"]),
    bad_input_check
)

print("\n=== NEGATIVE CONTROL: HYBRID WITHOUT EMBEDDING ===")
bad_hybrid=json.loads(json.dumps(hybrid))
bad_hybrid["knowledge"].pop("embedding",None)
bad_hybrid_check=registry.compatible(bad_hybrid)
add("registry_requires_embedding",
    bad_hybrid_check["ok"] is False
    and any(x.get("kind")=="embedding_required" for x in bad_hybrid_check["problems"]),
    bad_hybrid_check
)

print("\n=== NEGATIVE CONTROL: UNKNOWN TOOL PROFILE ===")
bad_tools=json.loads(json.dumps(spec))
bad_tools["tools"]="missing-tool-profile"
bad_tools_check=registry.compatible(bad_tools)
add("registry_blocks_unknown_tool_profile",
    bad_tools_check["ok"] is False
    and any(x.get("kind")=="registry_missing_tool_profile" for x in bad_tools_check["problems"]),
    bad_tools_check
)

print("\n=== CAPABILITY DISCOVERY ===")
brains=registry.list("brain")
coding=[x["id"] for x in brains if "coding" in x.get("capabilities",[])]
reasoning=[x["id"] for x in brains if "reasoning" in x.get("capabilities",[])]
add("capability_discovery",
    "qwen-coder" in coding and "deepseek-reasoning" in reasoning,
    {"coding":coding,"reasoning":reasoning}
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage27_block_registry.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
