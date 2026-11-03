import json
from pathlib import Path

class AgentZoo:
    def __init__(self, agents_dir):
        self.agents_dir=Path(agents_dir)

    def manifests(self):
        rows=[]
        for path in sorted(self.agents_dir.glob("*.json")):
            data=json.loads(path.read_text(encoding="utf-8"))
            rows.append({
                "agent_id":data["agent_id"],
                "brain_id":data["brain_id"],
                "competency_id":data["competency_id"],
                "knowledge":data.get("knowledge","folder"),
                "manifest_path":str(path)
            })
        return rows

    def get(self, agent_id):
        for item in self.manifests():
            if item["agent_id"]==agent_id:
                return item
        raise KeyError(agent_id)

    def health(self):
        rows=self.manifests()
        ids=[x["agent_id"] for x in rows]
        return {
            "status":"ok" if rows and len(ids)==len(set(ids)) else "error",
            "agents":len(rows),
            "unique_agent_ids":len(set(ids))
        }
