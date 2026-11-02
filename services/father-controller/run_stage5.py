import json, time, shutil
from pathlib import Path
from father.core.assembler import AgentAssembler
from father.core.io import ApiInputAdapter
from father.core.model_zoo import ModelZooDB
from father.core.scoring import score_response

BASE=Path(__file__).resolve().parent
brains_cfg=json.loads((BASE/"config/brains.json").read_text(encoding="utf-8"))["brains"]
assembler=AgentAssembler(BASE)
zoo=ModelZooDB(BASE/"data/model_zoo.db")
zoo.register_models(brains_cfg)
api=ApiInputAdapter()

all_rows=[]
for pack_id in ["generic","ib_demo"]:
    pack=assembler.competency(pack_id)
    for test in pack.tests:
        for brain_id in brains_cfg:
            agent,_=assembler.assemble(BASE/"config/agents/father_lab.json")
            selected_pack=assembler.competency(pack_id)
            from father.core.knowledge import FolderKnowledge
            agent.apply_competency(selected_pack, FolderKnowledge(selected_pack.knowledge_dir))
            agent.swap_brain(assembler.brain(brain_id))

            t0=time.perf_counter()
            result=agent.run(api.normalize({"content":test["prompt"]}))
            elapsed=int((time.perf_counter()-t0)*1000)
            quality=score_response(result.content,test["rubric"])

            zoo.record_run(
                brain_id,agent.agent_id,agent.competency_id,
                test["id"],test["task_type"],result,elapsed,quality
            )

            row={
                "pack":pack_id,
                "task_id":test["id"],
                "task_type":test["task_type"],
                "brain_id":brain_id,
                "ok":result.ok,
                "quality_score":quality["score"],
                "quality_passed":quality["passed"],
                "elapsed_ms":elapsed,
                "response":result.content,
                "scoring":quality
            }
            all_rows.append(row)
            print(json.dumps(row,ensure_ascii=False))

rank_arch=zoo.ranking("architecture")
rank_ib=zoo.ranking("ib-knowledge")

print("\n=== RANKING architecture ===")
print(json.dumps(rank_arch,ensure_ascii=False,indent=2))
print("\n=== RANKING ib-knowledge ===")
print(json.dumps(rank_ib,ensure_ascii=False,indent=2))

evidence={
    "stage":"FATHER Chassis v1.4 / Stage 5",
    "scorer":"deterministic-rubric-v1",
    "runs":len(all_rows),
    "architecture_ranking":rank_arch,
    "ib_ranking":rank_ib,
    "result":"PASS" if len(all_rows)>=12 and len(rank_arch)>=4 and len(rank_ib)>=4 else "FAIL"
}
(BASE/"evidence/stage5_evidence.json").write_text(
    json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8"
)
print("\nRESULT:",evidence["result"])
print("EVIDENCE:",BASE/"evidence/stage5_evidence.json")
raise SystemExit(0 if evidence["result"]=="PASS" else 1)
