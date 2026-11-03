import json
from pathlib import Path

class PolicyGate:
    def __init__(self, policy_path):
        self.policy_path=Path(policy_path)
        self.config=json.loads(self.policy_path.read_text(encoding="utf-8"))

    def _profile(self, agent_id):
        profiles=self.config.get("agents",{})
        if agent_id in profiles:
            return profiles[agent_id]
        return self.config.get("default",{})

    def check_agent(self, agent_id, task_type):
        profile=self._profile(agent_id)
        denied=set(profile.get("deny_task_types",[]))
        allowed=profile.get("allow_task_types",["*"])
        ok=(task_type not in denied) and ("*" in allowed or task_type in allowed)
        return {
            "kind":"agent",
            "agent_id":agent_id,
            "task_type":task_type,
            "allowed":bool(ok),
            "reason":"allowed" if ok else "task_type_denied"
        }

    def check_tool(self, agent_id, tool_name):
        profile=self._profile(agent_id)
        denied=set(profile.get("deny_tools",[]))
        allowed=profile.get("allow_tools",["*"])
        ok=(tool_name not in denied) and ("*" in allowed or tool_name in allowed)
        return {
            "kind":"tool",
            "agent_id":agent_id,
            "tool_name":tool_name,
            "allowed":bool(ok),
            "reason":"allowed" if ok else "tool_denied"
        }

    def health(self):
        return {
            "status":"ok",
            "agents":len(self.config.get("agents",{})),
            "has_default":bool(self.config.get("default"))
        }
