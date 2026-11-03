import json
from pathlib import Path
from father.core.provenance import digest

class ReleaseManifest:
    def __init__(self,base_dir):
        self.base=Path(base_dir)

    def _json(self,rel):
        return json.loads((self.base/rel).read_text(encoding="utf-8"))

    def build(self,version,anchor_commit):
        brains=self._json("config/brains.json")["brains"]
        routes=self._json("config/agent_routes.json")
        policies=self._json("config/policies.json")
        anchor=self._json("config/anchors/stage17_anchor_committed.json")

        agents=[]
        for p in sorted((self.base/"config/agents").glob("*.json")):
            m=json.loads(p.read_text(encoding="utf-8"))
            agents.append({
                "agent_id":m["agent_id"],
                "brain_id":m["brain_id"],
                "competency_id":m["competency_id"],
                "knowledge":m.get("knowledge","folder")
            })

        manifest={
            "release_version":version,
            "chassis_version":"2.8",
            "verified_through_stage":19,
            "brains":brains,
            "agents":agents,
            "routes":routes,
            "policies":policies,
            "external_anchor":{
                "commit":anchor_commit,
                "payload":anchor
            }
        }
        manifest["manifest_digest"]=digest({
            k:v for k,v in manifest.items() if k!="manifest_digest"
        })
        return manifest

    @staticmethod
    def compatibility(manifest):
        brains=set(manifest.get("brains",{}))
        agents=manifest.get("agents",[])
        agent_ids={a["agent_id"] for a in agents}
        problems=[]

        for a in agents:
            if a["brain_id"] not in brains:
                problems.append({
                    "kind":"missing_brain",
                    "agent_id":a["agent_id"],
                    "brain_id":a["brain_id"]
                })

        routes=manifest.get("routes",{})
        refs=set(routes.get("routes",{}).values())
        default=routes.get("default_agent_id")
        if default:
            refs.add(default)
        for agent_id in sorted(refs-agent_ids):
            problems.append({
                "kind":"missing_routed_agent",
                "agent_id":agent_id
            })

        policy_agents=set(manifest.get("policies",{}).get("agents",{}))
        for agent_id in sorted(agent_ids-policy_agents):
            problems.append({
                "kind":"missing_policy",
                "agent_id":agent_id
            })

        anchor=manifest.get("external_anchor",{})
        payload=anchor.get("payload",{})
        if not anchor.get("commit"):
            problems.append({"kind":"missing_anchor_commit"})
        if not payload.get("ledger_head_hash"):
            problems.append({"kind":"missing_anchor_head"})

        return {
            "ok":not problems,
            "agents":len(agents),
            "brains":len(brains),
            "routes":len(routes.get("routes",{})),
            "problems":problems
        }

    @staticmethod
    def verify_digest(manifest):
        expected=digest({
            k:v for k,v in manifest.items() if k!="manifest_digest"
        })
        return {
            "ok":manifest.get("manifest_digest")==expected,
            "expected":expected,
            "actual":manifest.get("manifest_digest")
        }
