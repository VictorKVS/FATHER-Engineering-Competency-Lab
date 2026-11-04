import json
from copy import deepcopy
from pathlib import Path

from father.core.block_registry import BlockRegistry

class DesignProjectError(RuntimeError):
    pass

class DesignStudioProject:
    def __init__(self,base_dir,project):
        self.base=Path(base_dir)
        self.project=deepcopy(project)
        self.registry=BlockRegistry(
            self.base/"config/blocks.json",
            self.base/"config/contracts/block_contract_v1.json"
        )

    @classmethod
    def load(cls,base_dir,path):
        base=Path(base_dir)
        p=Path(path)
        if not p.is_absolute():
            p=base/p
        return cls(base,json.loads(p.read_text(encoding="utf-8")))

    def validate(self):
        problems=[]
        p=self.project
        for field in ["project_id","name","chassis","nodes","edges","product"]:
            if field not in p:
                problems.append({"kind":"missing_project_field","field":field})

        nodes=p.get("nodes",[])
        node_ids=[x.get("node_id") for x in nodes]
        if len(node_ids)!=len(set(node_ids)):
            problems.append({"kind":"duplicate_node_id"})

        node_map={x.get("node_id"):x for x in nodes}
        for node in nodes:
            kind=node.get("kind")
            ref=node.get("ref")
            if kind=="agent":
                manifest=node.get("manifest")
                if not manifest:
                    problems.append({"kind":"agent_manifest_missing","node_id":node.get("node_id")})
                elif not (self.base/manifest).exists():
                    problems.append({"kind":"agent_manifest_not_found","node_id":node.get("node_id"),"manifest":manifest})
            elif kind=="block":
                block_type=node.get("block_type")
                if not self.registry.exists(block_type,ref):
                    problems.append({"kind":"registry_block_missing","node_id":node.get("node_id"),"block_type":block_type,"ref":ref})
            else:
                problems.append({"kind":"unsupported_node_kind","node_id":node.get("node_id"),"kind":kind})

        for edge in p.get("edges",[]):
            if edge.get("from") not in node_map:
                problems.append({"kind":"edge_source_missing","edge":edge})
            if edge.get("to") not in node_map:
                problems.append({"kind":"edge_target_missing","edge":edge})

        return {"ok":not problems,"nodes":len(nodes),"edges":len(p.get("edges",[])),"problems":problems}

    def graph(self):
        return {
            "project_id":self.project["project_id"],
            "chassis":self.project["chassis"],
            "nodes":deepcopy(self.project["nodes"]),
            "edges":deepcopy(self.project["edges"])
        }

    def export_product_spec(self):
        valid=self.validate()
        if not valid["ok"]:
            raise DesignProjectError(json.dumps(valid,ensure_ascii=False))

        product=deepcopy(self.project["product"])
        slots={}
        for node in self.project["nodes"]:
            if node.get("kind")=="block":
                slots.setdefault(node.get("block_type"),[]).append(node.get("ref"))
            elif node.get("kind")=="agent":
                slots["agent"]=[node.get("manifest")]

        if slots.get("agent"):
            product["agent_manifest"]=slots["agent"][0]
        if slots.get("brain"):
            product["brain_id"]=slots["brain"][0]
        if slots.get("competency"):
            product["competency_id"]=slots["competency"][0]
        if slots.get("input"):
            product["inputs"]=slots["input"]
        if slots.get("output"):
            product["outputs"]=slots["output"]
        if slots.get("knowledge"):
            knowledge=deepcopy(product.get("knowledge",{}))
            knowledge["adapter"]=slots["knowledge"][0]
            product["knowledge"]=knowledge
        if slots.get("tool_profile"):
            product["tools"]=slots["tool_profile"][0]

        return product

    def design_summary(self):
        return {
            "project_id":self.project["project_id"],
            "name":self.project["name"],
            "chassis":self.project["chassis"],
            "node_count":len(self.project.get("nodes",[])),
            "edge_count":len(self.project.get("edges",[])),
            "validation":self.validate(),
            "product_spec":self.export_product_spec() if self.validate()["ok"] else None
        }
