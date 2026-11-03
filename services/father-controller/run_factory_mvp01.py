import json
from pathlib import Path

from father.core.agent_zoo import AgentZoo

BASE=Path(__file__).resolve().parent
zoo=AgentZoo(
    BASE/"config/agent_zoo.json",
    BASE/"config/contracts/agent_contract_v1.json",
    base_dir=BASE
)

evidence={
    "milestone":"FATHER FACTORY MVP-01 / AGENT ZOO",
    "goal":"prove contract-driven Agent Zoo ready for Design Studio and Product Factory",
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== AGENT ZOO CONTRACT ===")
health=zoo.validate()
add("agent_zoo_contract_valid",health["ok"],health)

implemented=zoo.list()
implemented=[x for x in implemented if x["status"]!="planned"]
planned=zoo.list(status="planned")

add("implemented_agents_present",
    len(implemented)>=5,
    {
        "count":len(implemented),
        "agents":[{"id":x["agent_id"],"role":x["role"],"status":x["status"]} for x in implemented]
    }
)

add("planned_roles_seeded",
    len(planned)>=8,
    {
        "count":len(planned),
        "roles":[x["role"] for x in planned]
    }
)

print("\n=== AGENT / BRAIN COMPATIBILITY ===")
cases=[
    ("father-general-agent","qwen-analysis",True),
    ("father-coder-agent","qwen-coder",True),
    ("father-edge-agent","llama-small",True),
    ("father-edge-agent","deepseek-reasoning",False),
]
for agent_id,brain_id,expected in cases:
    result=zoo.compatibility(agent_id,brain_id)
    add(
        "compat_"+agent_id+"_"+brain_id,
        result["ok"] is expected,
        result
    )

print("\n=== CAPABILITY DISCOVERY ===")
coding=zoo.capability_candidates("coding")
security=zoo.capability_candidates("security")
rag=zoo.capability_candidates("rag")

add("coding_agent_discovery",
    any(x["agent_id"]=="father-coder-agent" for x in coding),
    {"candidates":coding}
)
add("security_agent_discovery",
    any(x["agent_id"]=="father-ib-agent" for x in security),
    {"candidates":security}
)
add("rag_agent_discovery",
    any(x["agent_id"]=="father-general-agent" for x in rag),
    {"candidates":rag}
)

print("\n=== DESIGN STUDIO READINESS ===")
card_fields=[
    "name","version","role","status","capabilities","required_slots",
    "supported_brains","inputs","outputs","tool_profile","knowledge_profile",
    "memory_profile","security_profile","tests","benchmarks"
]
sample=zoo.get("father-general-agent")
missing=[x for x in card_fields if x not in sample]
add("agent_card_complete",
    not missing,
    {"agent_id":"father-general-agent","missing":missing,"card":sample}
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/factory_mvp01_agent_zoo.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
