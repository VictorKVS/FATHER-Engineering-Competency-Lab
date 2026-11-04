import json
import importlib.util
from pathlib import Path

from father.core.design_studio import DesignStudioProject

BASE=Path(__file__).resolve().parent
WEB=BASE/"design_studio_web"

evidence={
  "milestone":"FATHER FACTORY MVP-07 / DESIGN STUDIO UI",
  "goal":"prove visual Design Studio assets and live catalog/project API backend are wired to existing factory contracts",
  "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== WEB ASSETS ===")
required=["index.html","styles.css","app.js"]
missing=[x for x in required if not (WEB/x).exists()]
add("web_assets_present",not missing,{"required":required,"missing":missing})

html=(WEB/"index.html").read_text(encoding="utf-8")
js=(WEB/"app.js").read_text(encoding="utf-8")
add("engineering_workspace_present",
    all(x in html for x in ["COMPONENTS","DESIGN CANVAS","INSPECTOR","COMPATIBILITY","Auto Complete"]),
    {"markers":["COMPONENTS","DESIGN CANVAS","INSPECTOR","COMPATIBILITY","Auto Complete"]}
)
add("canvas_interactions_present",
    all(x in js for x in ["dragstart","drop","/api/catalog","/api/validate-design","/api/auto-assemble"]),
    {"features":["drag-drop","catalog-api","validation-api","auto-assembly-api"]}
)

print("\n=== LIVE BACKEND CATALOG ===")
spec=importlib.util.spec_from_file_location("design_studio_server",BASE/"design_studio_server.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
cat=mod.catalog()
add("live_agent_catalog",
    len(cat["agents"])>=14 and cat["agent_health"]["ok"],
    {"agents":len(cat["agents"]),"health":cat["agent_health"]}
)
add("live_block_catalog",
    len(cat["blocks"])>=14 and cat["block_health"]["status"]=="ok",
    {"blocks":len(cat["blocks"]),"health":cat["block_health"]}
)

print("\n=== REFERENCE DESIGN ===")
project=DesignStudioProject.load(BASE,"config/design_projects/father_general_design.json")
validation=project.validate()
spec_out=project.export_product_spec() if validation["ok"] else None
add("reference_design_compiles",
    validation["ok"] and spec_out and spec_out["brain_id"]=="qwen-analysis",
    {"validation":validation,"product_spec":spec_out}
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
out=BASE/"evidence/factory_mvp07_design_studio_ui.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
