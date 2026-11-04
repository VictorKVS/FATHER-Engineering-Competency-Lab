import json
from pathlib import Path

class AgentZoo:
    def __init__(self,zoo_path,contract_path=None,base_dir=None):
        self.zoo_path=Path(zoo_path)
        self.base=Path(base_dir) if base_dir else self.zoo_path.parent.parent
        self.data=json.loads(self.zoo_path.read_text(encoding="utf-8"))
        self.agents=self.data.get("agents",{})
        self.contract={}
        if contract_path:
            self.contract=json.loads(Path(contract_path).read_text(encoding="utf-8"))

    def get(self,agent_id):
        return self.agents[agent_id]

    def list(self,status=None,capability=None):
        rows=[]
        for agent_id,meta in self.agents.items():
            if status and meta.get("status")!=status:
                continue
            if capability and capability not in meta.get("capabilities",[]):
                continue
            rows.append({"agent_id":agent_id,**meta})
        return sorted(rows,key=lambda x:x["agent_id"])

    def validate(self):
        required=self.contract.get("required",[])
        allowed_status=set(self.contract.get("lifecycle_status",[]))
        problems=[]
        roles=set()

        for agent_id,meta in self.agents.items():
            effective={"agent_id":agent_id,**meta}
            for field in required:
                if field not in effective:
                    problems.append({"kind":"missing_field","agent_id":agent_id,"field":field})

            if allowed_status and meta.get("status") not in allowed_status:
                problems.append({
                    "kind":"invalid_status",
                    "agent_id":agent_id,
                    "status":meta.get("status")
                })

            if meta.get("role"):
                roles.add(meta["role"])

            manifest=meta.get("manifest")
            if meta.get("status")!="planned":
                if not manifest:
                    problems.append({
                        "kind":"implemented_agent_missing_manifest",
                        "agent_id":agent_id
                    })
                else:
                    p=self.base/manifest
                    if not p.exists():
                        problems.append({
                            "kind":"manifest_not_found",
                            "agent_id":agent_id,
                            "manifest":str(p)
                        })
                    else:
                        data=json.loads(p.read_text(encoding="utf-8"))
                        if data.get("agent_id")!=agent_id:
                            problems.append({
                                "kind":"manifest_agent_id_mismatch",
                                "agent_id":agent_id,
                                "manifest_agent_id":data.get("agent_id")
                            })

        return {
            "ok":not problems,
            "agents":len(self.agents),
            "roles":len(roles),
            "implemented":len([1 for x in self.agents.values() if x.get("status")!="planned"]),
            "planned":len([1 for x in self.agents.values() if x.get("status")=="planned"]),
            "problems":problems
        }

    def compatibility(self,agent_id,brain_id):
        meta=self.get(agent_id)
        supported=meta.get("supported_brains",[])
        return {
            "ok":brain_id in supported,
            "agent_id":agent_id,
            "brain_id":brain_id,
            "supported_brains":supported
        }

    def capability_candidates(self,capability,statuses=None):
        statuses=set(statuses or ["experimental","tested","approved"])
        rows=[]
        for agent_id,meta in self.agents.items():
            if meta.get("status") not in statuses:
                continue
            if capability in meta.get("capabilities",[]):
                rows.append({
                    "agent_id":agent_id,
                    "role":meta.get("role"),
                    "status":meta.get("status"),
                    "supported_brains":meta.get("supported_brains",[])
                })
        return sorted(rows,key=lambda x:(x["status"],x["agent_id"]))
