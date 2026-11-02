import json
from pathlib import Path
from father.adapters.ollama import OllamaBrain
from father.core.agent import AgentChassis
from father.core.knowledge import FolderKnowledge, NullKnowledge
from father.core.prompt import PromptSlot
from father.core.tools import default_tools
from father.core.competency import CompetencyPack

class AgentAssembler:
    def __init__(self,base_dir):
        self.base=Path(base_dir)
        self.brains=json.loads((self.base/"config/brains.json").read_text(encoding="utf-8"))["brains"]
    def brain(self,brain_id):
        c=self.brains[brain_id]
        return OllamaBrain(brain_id,c["model"],c["base_url"])
    def competency(self,pack_id):
        return CompetencyPack(str(self.base/"config/competency_packs"/pack_id))
    def assemble(self,manifest_path):
        m=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        pack=self.competency(m["competency_id"])
        kb=FolderKnowledge(pack.knowledge_dir) if m.get("knowledge","folder")=="folder" else NullKnowledge()
        agent=AgentChassis(m["agent_id"],self.brain(m["brain_id"]),kb,default_tools(),PromptSlot())
        agent.apply_competency(pack,kb)
        return agent,m
