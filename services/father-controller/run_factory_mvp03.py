import json
from pathlib import Path

from father.core.design_studio import DesignStudioProject, DesignProjectError
from father.core.product_factory import ProductFactory

BASE=Path(__file__).resolve().parent
project=DesignStudioProject.load(BASE,"config/design_projects/father_general_design.json")
factory=ProductFactory(BASE)

evidence={
    "milestone":"FATHER FACTORY MVP-03 / DESIGN STUDIO DATA MODEL",
    "goal":"prove visual-design data model can validate a canvas graph and export a buildable Product Spec",
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== DESIGN PROJECT VALIDATION ===")
valid=project.validate()
add("design_project_valid",valid["ok"] and valid["nodes"]>=9 and valid["edges"]>=8,valid)

print("\n=== GRAPH MODEL ===")
graph=project.graph()
node_ids={x["node_id"] for x in graph["nodes"]}
add("canvas_graph_complete",
    {"input-api","agent-main","brain-main","knowledge-main","output-json"}.issubset(node_ids),
    {"chassis":graph["chassis"],"nodes":len(graph["nodes"]),"edges":len(graph["edges"])}
)

print("\n=== PRODUCT SPEC EXPORT ===")
spec=project.export_product_spec()
add("product_spec_exported",
    spec["brain_id"]=="qwen-analysis"
    and spec["competency_id"]=="generic"
    and sorted(spec["inputs"])==["api","file"]
    and sorted(spec["outputs"])==["file","json"]
    and spec["knowledge"]["adapter"]=="folder"
    and spec["tools"]=="default",
    spec
)

print("\n=== FACTORY COMPATIBILITY ===")
validation=factory.validate(spec)
add("exported_spec_factory_compatible",validation["ok"],validation)

built=factory.build(spec)
add("design_to_product_build",
    built["report"]["status"]=="ready"
    and built["report"]["brain_id"]=="qwen-analysis",
    built["report"]
)

print("\n=== NEGATIVE CONTROLS ===")
bad=json.loads(json.dumps(project.project))
bad["nodes"]=[x for x in bad["nodes"] if x["node_id"]!="brain-main"]
bad["edges"].append({"from":"missing-node","to":"agent-main","relation":"feeds"})
bad_project=DesignStudioProject(BASE,bad)
bad_validation=bad_project.validate()
add("broken_graph_rejected",
    bad_validation["ok"] is False
    and any(x.get("kind")=="edge_source_missing" for x in bad_validation["problems"]),
    bad_validation
)

missing=json.loads(json.dumps(project.project))
for node in missing["nodes"]:
    if node.get("node_id")=="knowledge-main":
        node["ref"]="missing-knowledge"
missing_project=DesignStudioProject(BASE,missing)
missing_validation=missing_project.validate()
add("missing_registry_block_rejected",
    missing_validation["ok"] is False
    and any(x.get("kind")=="registry_block_missing" for x in missing_validation["problems"]),
    missing_validation
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
out=BASE/"evidence/factory_mvp03_design_studio_model.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
