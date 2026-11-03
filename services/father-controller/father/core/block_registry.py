import json
from pathlib import Path

class BlockRegistry:
    def __init__(self,path):
        self.path=Path(path)
        self.data=json.loads(self.path.read_text(encoding="utf-8"))
        self.blocks=self.data.get("blocks",{})

    def health(self):
        ids=[]
        problems=[]
        for block_type,items in self.blocks.items():
            for block_id,meta in items.items():
                ids.append((block_type,block_id))
                if meta.get("type") and meta.get("type")!=block_type:
                    problems.append({
                        "kind":"type_mismatch",
                        "block_type":block_type,
                        "block_id":block_id,
                        "declared":meta.get("type")
                    })
        return {
            "status":"ok" if self.blocks and not problems else "error",
            "types":sorted(self.blocks),
            "blocks":len(ids),
            "problems":problems
        }

    def exists(self,block_type,block_id):
        return block_id in self.blocks.get(block_type,{})

    def get(self,block_type,block_id):
        return self.blocks[block_type][block_id]

    def list(self,block_type=None):
        if block_type:
            return [
                {"id":k,**v}
                for k,v in sorted(self.blocks.get(block_type,{}).items())
            ]
        out=[]
        for t,items in self.blocks.items():
            for k,v in items.items():
                out.append({"type":t,"id":k,**v})
        return sorted(out,key=lambda x:(x["type"],x["id"]))

    def compatible(self,spec):
        problems=[]

        brain_id=spec.get("brain_id")
        if not self.exists("brain",brain_id):
            problems.append({"kind":"registry_missing_brain","brain_id":brain_id})

        competency_id=spec.get("competency_id")
        if not self.exists("competency",competency_id):
            problems.append({"kind":"registry_missing_competency","competency_id":competency_id})

        knowledge=(spec.get("knowledge") or {}).get("adapter")
        if not self.exists("knowledge",knowledge):
            problems.append({"kind":"registry_missing_knowledge","adapter":knowledge})

        for name in spec.get("inputs",[]):
            if not self.exists("input",name):
                problems.append({"kind":"registry_missing_input","adapter":name})

        for name in spec.get("outputs",[]):
            if not self.exists("output",name):
                problems.append({"kind":"registry_missing_output","adapter":name})

        tool_profile=spec.get("tools","default")
        if not self.exists("tool_profile",tool_profile):
            problems.append({"kind":"registry_missing_tool_profile","profile":tool_profile})

        if knowledge=="hybrid-folder":
            meta=self.get("knowledge","hybrid-folder")
            embed=(spec.get("knowledge") or {}).get("embedding") or {}
            if meta.get("requires_embedding") and not embed.get("model"):
                problems.append({
                    "kind":"embedding_required",
                    "knowledge":"hybrid-folder"
                })

        return {"ok":not problems,"problems":problems}
