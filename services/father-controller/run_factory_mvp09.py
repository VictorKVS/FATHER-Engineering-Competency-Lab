import json
import shutil
from pathlib import Path

from father.core.model_intelligence import ModelIntelligenceRegistry

BASE=Path(__file__).resolve().parent
src=BASE/"config/model_intelligence.json"
tmp=BASE/"evidence/model_intelligence_mvp09_tmp.json"
tmp.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(src,tmp)
reg=ModelIntelligenceRegistry(tmp)

evidence={
  "milestone":"FATHER FACTORY MVP-09 / MODEL MATRIX ECONOMICS LEAGUE",
  "goal":"prove multidimensional model matrix, economic profiles and CHAMPION/CHALLENGER/BASELINE league mechanics",
  "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== APPLICATION MATRIX ===")
matrix=reg.application_matrix()
add("matrix_has_models",
    len(matrix)>=6
    and all("deployment" in x and "commercial_use" in x and "resource_class" in x for x in matrix),
    {"rows":matrix}
)

print("\n=== ECONOMICS ENGINE ===")
profile=reg.add_economic_profile("qwen-analysis",{
    "profile_id":"mvp09-commercial-rag",
    "name":"commercial-rag",
    "requests_per_month":1000,
    "human_minutes_per_task":20,
    "human_hourly_cost":1200,
    "review_minutes_per_task":3,
    "local_fixed_monthly_cost":3000,
    "local_variable_cost_per_task":1,
    "cloud_cost_per_task":8,
    "api_cost_per_task":15
})
add("economics_calculated",
    profile["manual_monthly_cost"]==400000.0
    and profile["best_deployment"]=="local"
    and profile["best_monthly_saving"]>0,
    profile
)

print("\n=== MODEL LEAGUE ===")
reg.set_league_role("qwen-analysis","rag","CHAMPION",98)
reg.set_league_role("llama-small","rag","BASELINE",60)
reg.set_league_role("deepseek-reasoning","rag","CHALLENGER",75)
league=reg.league("rag")
add("league_three_roles",
    [x["role"] for x in league[:3]]==["CHAMPION","CHALLENGER","BASELINE"]
    and {x["model_id"] for x in league[:3]}=={"qwen-analysis","deepseek-reasoning","llama-small"},
    {"league":league}
)

print("\n=== DESIGN STUDIO INTEGRATION ===")
html=(BASE/"design_studio_web/index.html").read_text(encoding="utf-8")
js=(BASE/"design_studio_web/app.js").read_text(encoding="utf-8")
server=(BASE/"design_studio_server.py").read_text(encoding="utf-8")
markers=[
    "ECONOMICS PROFILE","MODEL LEAGUE","Show Application Matrix",
    "/economics","/league","/api/models/matrix"
]
combined=html+"\n"+js+"\n"+server
missing=[x for x in markers if x not in combined]
add("site_matrix_economics_league_present",not missing,{"missing":missing})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
out=BASE/"evidence/factory_mvp09_model_matrix.json"
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
try: tmp.unlink()
except Exception: pass

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
