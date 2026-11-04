import json
from pathlib import Path

from father.core.block_registry import BlockRegistry

BASE=Path(__file__).resolve().parent
registry=BlockRegistry(
    BASE/"config/blocks.json",
    BASE/"config/contracts/block_contract_v1.json"
)

evidence={
    "milestone":"FATHER FACTORY MVP-02 / BLOCK CONTRACT",
    "goal":"prove industrial block contract and Design Studio-ready registry metadata",
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== BLOCK REGISTRY HEALTH ===")
health=registry.health()
add("registry_health",
    health["status"]=="ok" and health.get("registry_version")=="2.0",
    health
)

print("\n=== BLOCK CONTRACT ===")
contract=registry.contract_health()
add("block_contract_valid",
    contract["ok"] and contract["blocks"]>=14,
    contract
)

print("\n=== DESIGN STUDIO CARDS ===")
sample=registry.card("brain","qwen-analysis")
required_card=[
    "id","type","version","status","capabilities","inputs","outputs",
    "dependencies","resources","permissions","security","tests","compatibility"
]
missing=[x for x in required_card if x not in sample]
add("block_card_complete",
    not missing,
    {"missing":missing,"card":sample}
)

print("\n=== CAPABILITY DISCOVERY ===")
analysis=registry.capability_candidates("analysis","brain")
rag=registry.capability_candidates("rag")
json_blocks=registry.capability_candidates("json")
add("analysis_capability_discovery",
    any(x["id"]=="qwen-analysis" for x in analysis),
    {"candidates":analysis}
)
add("rag_capability_discovery",
    any(x["id"]=="qwen-analysis" for x in rag),
    {"candidates":rag}
)
add("json_capability_discovery",
    any(x["type"]=="input" and x["id"]=="api" for x in json_blocks)
    and any(x["type"]=="output" and x["id"]=="json" for x in json_blocks),
    {"candidates":json_blocks}
)

print("\n=== PRODUCT COMPATIBILITY PRESERVED ===")
spec=json.loads((BASE/"config/products/father_general_single.json").read_text(encoding="utf-8"))
compat=registry.compatible(spec)
add("existing_product_compatible",
    compat["ok"],
    compat
)

print("\n=== NEGATIVE CONTROL ===")
bad=json.loads(json.dumps(spec))
bad["inputs"]=list(bad.get("inputs",[]))+["missing-design-input"]
bad_compat=registry.compatible(bad)
add("unknown_block_rejected",
    bad_compat["ok"] is False
    and any(x.get("kind")=="registry_missing_input" for x in bad_compat["problems"]),
    bad_compat
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/factory_mvp02_block_contract.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
