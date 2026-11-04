import json
from copy import deepcopy
from pathlib import Path

from father.core.agent_zoo import AgentZoo
from father.core.block_registry import BlockRegistry
from father.core.model_applicability import ModelApplicabilityEngine

class AutoAssemblyPlanner:
    def __init__(self,base_dir):
        self.base=Path(base_dir)
        self.agents=AgentZoo(
            self.base/"config/agent_zoo.json",
            self.base/"config/contracts/agent_contract_v1.json",
            base_dir=self.base
        )
        self.blocks=BlockRegistry(
            self.base/"config/blocks.json",
            self.base/"config/contracts/block_contract_v1.json"
        )
        self.models=ModelApplicabilityEngine(self.base/"config/model_knowledge_base.json")

    def _implemented_agent_rows(self):
        return [
            x for x in self.agents.list()
            if x.get("status") in {"experimental","tested","approved"}
        ]

    def _planned_agent_rows(self):
        return self.agents.list(status="planned")

    def choose_agent(self,required_capabilities):
        required=set(required_capabilities or [])
        candidates=[]
        for row in self._implemented_agent_rows():
            caps=set(row.get("capabilities",[]))
            covered=sorted(required & caps)
            score=len(covered)
            candidates.append({
                "agent_id":row["agent_id"],
                "manifest":row.get("manifest"),
                "status":row.get("status"),
                "covered":covered,
                "missing":sorted(required-caps),
                "score":score,
                "supported_brains":row.get("supported_brains",[])
            })
        candidates.sort(key=lambda x:(-x["score"],x["status"]!="tested",x["agent_id"]))
        return candidates[0] if candidates else None

    def gap_analysis(self,requirements):
        required_caps=set(requirements.get("capabilities",[]))
        implemented=self._implemented_agent_rows()
        planned=self._planned_agent_rows()

        implemented_caps=set()
        for row in implemented:
            implemented_caps.update(row.get("capabilities",[]))
        planned_caps=set()
        for row in planned:
            planned_caps.update(row.get("capabilities",[]))

        reuse=[]
        adapt=[]
        build=[]

        for cap in sorted(required_caps):
            if cap in implemented_caps:
                reuse.append({"kind":"capability","id":cap,"source":"implemented_agent"})
            elif cap in planned_caps:
                adapt.append({"kind":"capability","id":cap,"source":"planned_agent"})
            else:
                block_hits=self.blocks.capability_candidates(cap)
                if block_hits:
                    reuse.append({"kind":"capability","id":cap,"source":"block_registry","candidates":block_hits})
                else:
                    build.append({"kind":"capability","id":cap,"reason":"no_agent_or_block_candidate"})

        for name in requirements.get("inputs",[]):
            if self.blocks.exists("input",name):
                reuse.append({"kind":"input","id":name})
            else:
                build.append({"kind":"input","id":name,"reason":"missing_input_block"})

        for name in requirements.get("outputs",[]):
            if self.blocks.exists("output",name):
                reuse.append({"kind":"output","id":name})
            else:
                build.append({"kind":"output","id":name,"reason":"missing_output_block"})

        knowledge=requirements.get("knowledge","folder")
        if self.blocks.exists("knowledge",knowledge):
            reuse.append({"kind":"knowledge","id":knowledge})
        else:
            build.append({"kind":"knowledge","id":knowledge,"reason":"missing_knowledge_block"})

        tools=requirements.get("tools","default")
        if self.blocks.exists("tool_profile",tools):
            reuse.append({"kind":"tool_profile","id":tools})
        else:
            build.append({"kind":"tool_profile","id":tools,"reason":"missing_tool_profile"})

        return {"reuse":reuse,"adapt":adapt,"build":build}

    def plan(self,requirements):
        agent_choice=self.choose_agent(requirements.get("capabilities",[]))
        gaps=self.gap_analysis(requirements)

        task={
            "text":requirements.get("task",""),
            "modality":requirements.get("modality","text"),
            "specialization":requirements.get("specialization","general"),
            "complexity":requirements.get("complexity",2)
        }
        model_decision=self.models.choose(task,registered_only=True)
        selected_model=model_decision.get("selected")

        problems=[]
        if not agent_choice:
            problems.append({"kind":"no_implemented_agent"})
        if not selected_model:
            problems.append({"kind":"no_registered_brain"})
        if agent_choice and selected_model:
            compat=self.agents.compatibility(agent_choice["agent_id"],selected_model["brain_id"])
            if not compat["ok"]:
                fallback=None
                for brain_id in agent_choice.get("supported_brains",[]):
                    if self.blocks.exists("brain",brain_id):
                        fallback=brain_id
                        break
                if fallback:
                    selected_model=deepcopy(selected_model)
                    selected_model["brain_id"]=fallback
                    selected_model["selection_note"]="fallback_to_agent_supported_brain"
                else:
                    problems.append({"kind":"agent_brain_incompatible","agent_id":agent_choice["agent_id"]})

        blockers=[x for x in gaps["build"] if x.get("kind") in {"input","output","knowledge","tool_profile"}]

        product_spec=None
        if not problems and not blockers:
            product_spec={
                "product_id":requirements.get("product_id","father-auto-product-v1"),
                "agent_manifest":agent_choice["manifest"],
                "brain_id":selected_model["brain_id"],
                "competency_id":requirements.get("competency_id","generic"),
                "inputs":list(requirements.get("inputs",["api"])),
                "outputs":list(requirements.get("outputs",["json"])),
                "knowledge":{"adapter":requirements.get("knowledge","folder")},
                "retrieval":{"top_k":int(requirements.get("top_k",5))},
                "tools":requirements.get("tools","default"),
                "context_bus":True
            }

        return {
            "ok":not problems and not blockers,
            "requirements":requirements,
            "agent_choice":agent_choice,
            "model_choice":selected_model,
            "model_ranking":model_decision.get("ranking",[])[:4],
            "gaps":gaps,
            "blockers":blockers,
            "problems":problems,
            "product_spec":product_spec
        }
