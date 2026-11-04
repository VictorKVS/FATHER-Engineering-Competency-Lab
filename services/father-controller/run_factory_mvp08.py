import json
import shutil
from pathlib import Path

from father.core.model_intelligence import ModelIntelligenceRegistry

BASE=Path(__file__).resolve().parent
source=BASE/"config/model_intelligence.json"
tmp=BASE/"evidence/model_intelligence_mvp08_tmp.json"
tmp.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,tmp)
reg=ModelIntelligenceRegistry(tmp)

evidence={
  "milestone":"FATHER FACTORY MVP-08 / MODEL INTELLIGENCE",
  "goal":"prove model creation, provenance filling, verification state and Design Studio integration",
  "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== REGISTRY HEALTH ===")
health=reg.health()
add("registry_health",health["ok"] and health["models"]>=6,health)

print("\n=== CREATE CANDIDATE ===")
candidate=reg.create_candidate({
    "model_id":"mvp08-candidate",
    "provider":"test-provider",
    "runtime_model":"test:model",
    "version":"1.0",
    "deployment":["local"]
})
add("candidate_created",
    candidate["admission_status"]=="DISCOVERED"
    and candidate["lifecycle"]=="candidate",
    candidate
)

print("\n=== VERIFIED SOURCE CLAIMS ===")
claims=[
    {"field":"license","value":"Apache-2.0","source_url":"https://example.invalid/license","source_class":"OFFICIAL_PRIMARY","verification_status":"SOURCE_CONFIRMED","confidence":"HIGH"},
    {"field":"commercial_use","value":"ALLOWED","source_url":"https://example.invalid/license","source_class":"OFFICIAL_PRIMARY","verification_status":"SOURCE_CONFIRMED","confidence":"HIGH"},
    {"field":"deployment","value":["local","private_cloud"],"source_url":"https://example.invalid/docs","source_class":"OFFICIAL_PRIMARY","verification_status":"SOURCE_CONFIRMED","confidence":"HIGH"},
    {"field":"context_window_tokens","value":131072,"source_url":"https://example.invalid/specs","source_class":"OFFICIAL_PRIMARY","verification_status":"SOURCE_CONFIRMED","confidence":"MEDIUM"}
]
for c in claims:
    reg.add_claim("mvp08-candidate",c)
record=reg.get("mvp08-candidate")
summary=reg.verification_summary("mvp08-candidate")
add("critical_facts_promoted",
    record["license"]["value"]=="Apache-2.0"
    and record["commercial_use"]=="ALLOWED"
    and "local" in record["deployment"]
    and record["context_window_tokens"]==131072,
    {"record":record,"summary":summary}
)
add("ready_for_bench_transition",
    record["admission_status"]=="READY_FOR_BENCH" and summary["bench_ready"],
    {"admission_status":record["admission_status"],"verification":summary}
)

print("\n=== CONFLICT CONTROL ===")
reg.add_claim("mvp08-candidate",{
    "field":"license",
    "value":"Commercial-only",
    "source_url":"https://example.invalid/conflict",
    "source_class":"INDEPENDENT_BENCHMARK",
    "verification_status":"CONFLICT",
    "confidence":"MEDIUM"
})
conflicted=reg.get("mvp08-candidate")
conf_summary=reg.verification_summary("mvp08-candidate")
add("conflict_detected",
    "license" in conf_summary["conflicts"]
    and conflicted["admission_status"]=="DATA_COLLECTION",
    {"admission_status":conflicted["admission_status"],"verification":conf_summary}
)

print("\n=== DESIGN STUDIO INTEGRATION ===")
html=(BASE/"design_studio_web/index.html").read_text(encoding="utf-8")
js=(BASE/"design_studio_web/app.js").read_text(encoding="utf-8")
server=(BASE/"design_studio_server.py").read_text(encoding="utf-8")
markers=[
    "Model Intelligence","CREATE CANDIDATE","SOURCE CLAIM",
    "/api/models/create","/api/models/","model_intelligence"
]
combined=html+"\n"+js+"\n"+server
missing=[x for x in markers if x not in combined]
add("design_studio_model_intelligence_present",not missing,{"missing":missing})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
out=BASE/"evidence/factory_mvp08_model_intelligence.json"
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
try: tmp.unlink()
except Exception: pass

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
