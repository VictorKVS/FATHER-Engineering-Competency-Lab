import json
from pathlib import Path

from father.core.assembler import AgentAssembler
from father.core.hybrid_knowledge import HybridFolderKnowledge, OllamaEmbeddingClient
from father.core.io import ApiInputAdapter, FileInputAdapter
from father.core.runtime_io import RuntimeJsonOutputAdapter, RuntimeFileOutputAdapter
from father.core.unified_runtime import UnifiedAgentRuntime

class FactoryBuildError(RuntimeError):
    pass

class ProductFactory:
    def __init__(self,base_dir):
        self.base=Path(base_dir)
        self.assembler=AgentAssembler(self.base)

    def load_spec(self,path):
        p=Path(path)
        if not p.is_absolute():
            p=self.base/p
        return json.loads(p.read_text(encoding="utf-8"))

    def validate(self,spec):
        problems=[]
        required=["product_id","agent_manifest","brain_id","competency_id","knowledge","inputs","outputs"]
        for key in required:
            if key not in spec:
                problems.append({"kind":"missing_field","field":key})

        if spec.get("brain_id") not in self.assembler.brains:
            problems.append({"kind":"unknown_brain","brain_id":spec.get("brain_id")})

        manifest_path=self.base/spec.get("agent_manifest","")
        if not manifest_path.exists():
            problems.append({"kind":"missing_agent_manifest","path":str(manifest_path)})

        try:
            self.assembler.competency(spec.get("competency_id",""))
        except Exception:
            problems.append({"kind":"missing_competency","competency_id":spec.get("competency_id")})

        supported_inputs={"api","file"}
        supported_outputs={"json","file"}
        for item in spec.get("inputs",[]):
            if item not in supported_inputs:
                problems.append({"kind":"unsupported_input","adapter":item})
        for item in spec.get("outputs",[]):
            if item not in supported_outputs:
                problems.append({"kind":"unsupported_output","adapter":item})

        knowledge_type=(spec.get("knowledge") or {}).get("adapter")
        if knowledge_type not in {"folder","hybrid-folder","null"}:
            problems.append({"kind":"unsupported_knowledge","adapter":knowledge_type})

        return {"ok":not problems,"problems":problems}

    def _knowledge(self,spec,agent):
        cfg=spec["knowledge"]
        adapter=cfg["adapter"]

        if adapter=="null":
            from father.core.knowledge import NullKnowledge
            return NullKnowledge()

        if adapter=="folder":
            return agent.knowledge

        if adapter=="hybrid-folder":
            corpus=self.base/cfg["corpus"]
            embed=cfg["embedding"]
            client=OllamaEmbeddingClient(
                model=embed["model"],
                base_url=embed.get("base_url","http://127.0.0.1:11434")
            )
            kb=HybridFolderKnowledge(
                corpus,
                client,
                chunk_chars=int(cfg.get("chunk_chars",1200)),
                semantic_weight=float(cfg.get("semantic_weight",0.7)),
                lexical_weight=float(cfg.get("lexical_weight",0.3))
            )
            kb.build_index()
            return kb

        raise FactoryBuildError("unsupported knowledge adapter: "+str(adapter))

    def _inputs(self,names):
        registry={
            "api":ApiInputAdapter,
            "file":FileInputAdapter
        }
        return {name:registry[name]() for name in names}

    def _outputs(self,names):
        registry={
            "json":RuntimeJsonOutputAdapter,
            "file":RuntimeFileOutputAdapter
        }
        return {name:registry[name]() for name in names}

    def build(self,spec):
        validation=self.validate(spec)
        if not validation["ok"]:
            raise FactoryBuildError(json.dumps(validation,ensure_ascii=False))

        agent,manifest=self.assembler.assemble(self.base/spec["agent_manifest"])

        if agent.brain.brain_id!=spec["brain_id"]:
            agent.swap_brain(self.assembler.brain(spec["brain_id"]))

        if agent.competency_id!=spec["competency_id"]:
            pack=self.assembler.competency(spec["competency_id"])
            agent.apply_competency(pack,agent.knowledge)

        knowledge=self._knowledge(spec,agent)
        agent.knowledge=knowledge

        runtime=UnifiedAgentRuntime(
            agent,
            top_k=int((spec.get("retrieval") or {}).get("top_k",5))
        )

        inputs=self._inputs(spec["inputs"])
        outputs=self._outputs(spec["outputs"])

        report={
            "product_id":spec["product_id"],
            "agent_id":agent.agent_id,
            "brain_id":agent.brain.brain_id,
            "competency_id":agent.competency_id,
            "prompt_loaded":bool(agent.prompt_slot.system_prompt),
            "knowledge":agent.knowledge.health(),
            "inputs":sorted(inputs),
            "outputs":sorted(outputs),
            "tools":[x["name"] for x in agent.tools.list()],
            "context_bus":bool(spec.get("context_bus",True)),
            "status":"ready"
        }

        return {
            "spec":spec,
            "manifest":manifest,
            "agent":agent,
            "runtime":runtime,
            "inputs":inputs,
            "outputs":outputs,
            "report":report
        }
