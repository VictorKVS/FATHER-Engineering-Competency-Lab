import json
import os
from pathlib import Path

from father.core.assembler import AgentAssembler
from father.core.preflight import ollama_preflight

BASE=Path(__file__).resolve().parent
assembler=AgentAssembler(BASE)

evidence={
    "stage":"FATHER Chassis v1.7 / Stage 8",
    "goal":"prove storage and model-zoo preflight before agent execution",
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== STORAGE + MODEL ZOO PREFLIGHT ===")
report=ollama_preflight(assembler.brains,min_free_gb=20)

for c in report["checks"]:
    add(c["name"],c["passed"],c["details"])

print("\n=== NEGATIVE CONTROL: MISSING STORAGE MUST FAIL ===")
original=os.environ.get("OLLAMA_MODELS")
try:
    os.environ["OLLAMA_MODELS"]=str(BASE/"data/__missing_model_store__")
    negative=ollama_preflight(assembler.brains,min_free_gb=20)
finally:
    if original is None:
        os.environ.pop("OLLAMA_MODELS",None)
    else:
        os.environ["OLLAMA_MODELS"]=original

negative_ok=not negative["passed"] and any(
    c["name"]=="storage_exists" and not c["passed"] for c in negative["checks"]
)
add("negative_missing_storage_detected",negative_ok,{
    "preflight_passed":negative["passed"],
    "checks":negative["checks"]
})

print("\n=== NEGATIVE CONTROL: MISSING MODEL MUST FAIL ===")
fake=json.loads(json.dumps(assembler.brains))
fake["missing-model-test"]={
    "adapter":"ollama",
    "model":"father-this-model-must-not-exist:stage8",
    "base_url":"http://127.0.0.1:11434"
}
missing_model_report=ollama_preflight(fake,min_free_gb=20)
missing_model_ok=not missing_model_report["passed"] and "father-this-model-must-not-exist:stage8" in missing_model_report["required_models"]["missing"]
add("negative_missing_model_detected",missing_model_ok,{
    "preflight_passed":missing_model_report["passed"],
    "missing":missing_model_report["required_models"]["missing"]
})

print("\n=== AGENT EXECUTION AFTER PREFLIGHT ===")
if report["passed"]:
    agent,_=assembler.assemble(BASE/"config/agents/father_lab.json")
    health=agent.brain.health()
    add("agent_allowed_after_preflight",health.get("status")=="ok",health)
else:
    add("agent_allowed_after_preflight",False,{
        "reason":"positive preflight failed; agent execution blocked"
    })

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
evidence["positive_preflight"]=report
evidence["negative_missing_storage"]=negative
evidence["negative_missing_model"]=missing_model_report

out=BASE/"evidence/stage8_evidence.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
