import json
from pathlib import Path

from father.core.assembler import AgentAssembler
from father.core.brain_experiments import BrainExperimentRunner
from father.core.io import ApiInputAdapter

BASE=Path(__file__).resolve().parent
CFG=json.loads((BASE/"config/experiments/brain_swap_generic.json").read_text(encoding="utf-8"))

assembler=AgentAssembler(BASE)
agent,_=assembler.assemble(BASE/CFG["agent_manifest"])
pack=assembler.competency(CFG["competency_id"])
api=ApiInputAdapter()
runner=BrainExperimentRunner(assembler,agent,top_k=5)

evidence={
    "stage":"FATHER Brain Experiments v1 / Stage 24",
    "goal":"prove automatic hot-swap benchmarking of multiple brains under frozen conditions",
    "config":CFG,
    "checks":[],
    "cases":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== EXPERIMENT CONFIG ===")
add("brains_registered",
    all(x in assembler.brains for x in CFG["brains"]),
    {"brains":CFG["brains"],"registered":sorted(assembler.brains)}
)

original_brain=agent.brain.brain_id
print("\n=== AUTOMATIC BRAIN SWAP CASES ===")

for test in pack.tests:
    event=api.normalize({
        "type":test["task_type"],
        "content":test["prompt"],
        "metadata":{"stage":24,"test_id":test["id"]}
    })
    case=runner.run_case(
        event,
        test["task_type"],
        test["rubric"],
        CFG["brains"]
    )
    case["test_id"]=test["id"]
    evidence["cases"].append(case)

    add("all_brains_ran_"+test["id"],
        len(case["results"])==len(CFG["brains"])
        and all("rank" in x for x in case["results"]),
        {
            "winner":case["winner"],
            "brains":[x["brain_id"] for x in case["results"]],
            "ranks":[{"brain_id":x["brain_id"],"rank":x["rank"]} for x in case["results"]]
        }
    )

    add("frozen_context_"+test["id"],
        case["frozen_context"]["knowledge_hits"]>0
        and len(case["frozen_context"]["messages"])>=2,
        {
            "knowledge_hits":case["frozen_context"]["knowledge_hits"],
            "knowledge_sources":case["frozen_context"]["knowledge_sources"],
            "message_count":len(case["frozen_context"]["messages"])
        }
    )

summary=runner.aggregate(evidence["cases"])
evidence["summary"]=summary

print("\n=== AGGREGATE RANKING ===")
for row in summary["ranking"]:
    print("RANK",row["rank"],json.dumps(row,ensure_ascii=False))

add("aggregate_ranking_created",
    len(summary["ranking"])==len(CFG["brains"]) and bool(summary["winner"]),
    summary
)

add("original_brain_restored",
    agent.brain.brain_id==original_brain,
    {"before":original_brain,"after":agent.brain.brain_id}
)

print("\n=== NEGATIVE CONTROL: INVALID BRAIN ===")
invalid_detected=False
try:
    assembler.brain("missing-stage24-brain")
except KeyError:
    invalid_detected=True
add("invalid_brain_rejected",invalid_detected,{"brain_id":"missing-stage24-brain"})

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"

out=BASE/"evidence/stage24_brain_experiments.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nWINNER:",summary["winner"])
print("RESULT:",evidence["result"])
print("EVIDENCE:",out)
raise SystemExit(0 if release else 1)
