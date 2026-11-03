import json
from pathlib import Path

class AgentRouter:
    def __init__(self, routes_path, zoo):
        self.routes_path=Path(routes_path)
        self.zoo=zoo
        self.config=json.loads(self.routes_path.read_text(encoding="utf-8"))
        self.routes=self.config.get("routes",{})
        self.default_agent_id=self.config.get("default_agent_id")

    def route(self, task_type):
        agent_id=self.routes.get(task_type,self.default_agent_id)
        if not agent_id:
            raise KeyError(f"no route for task_type={task_type}")
        manifest=self.zoo.get(agent_id)
        return {
            "task_type":task_type,
            "agent_id":agent_id,
            "manifest_path":manifest["manifest_path"],
            "brain_id":manifest["brain_id"],
            "competency_id":manifest["competency_id"],
            "fallback":task_type not in self.routes
        }

    def health(self):
        known={x["agent_id"] for x in self.zoo.manifests()}
        referenced=set(self.routes.values())
        if self.default_agent_id:
            referenced.add(self.default_agent_id)
        missing=sorted(referenced-known)
        return {
            "status":"ok" if not missing and bool(self.routes) else "error",
            "routes":len(self.routes),
            "default_agent_id":self.default_agent_id,
            "missing_agents":missing
        }
