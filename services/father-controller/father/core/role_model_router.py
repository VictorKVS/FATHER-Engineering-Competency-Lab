import json
from pathlib import Path

class RoleModelRouter:
    """Role-aware evidence router.

    This module does not replace Stage29 routing yet. It provides the next
    evidence layer: role -> gated candidates -> preferred runtime model.
    Promotion into the production router happens only after local acceptance.
    """
    def __init__(self, base_dir):
        self.base=Path(base_dir)
        self.path=self.base/"config/role_model_matrix.json"
        self.data=json.loads(self.path.read_text(encoding="utf-8"))

    def role(self, role_id):
        roles=self.data.get("roles",{})
        if role_id not in roles:
            return {"ok":False,"reason":"unknown_role","role":role_id}
        r=roles[role_id]
        ordered=[]
        for key in ("champion_candidate","challenger","baseline"):
            v=r.get(key)
            if v and v not in ordered:
                ordered.append(v)
        for v in r.get("challengers",[]) or []:
            if v not in ordered: ordered.append(v)
        for v in r.get("candidates",[]) or []:
            if v not in ordered: ordered.append(v)
        return {
          "ok":True,
          "role":role_id,
          "status":r.get("status","EVIDENCE_AVAILABLE"),
          "quality_gate":r.get("quality_gate"),
          "preferred":ordered[0] if ordered else None,
          "candidates":ordered,
          "notes":r.get("notes"),
          "evidence":r.get("evidence")
        }

    def choose(self, role_id, allow_unbenchmarked=False):
        result=self.role(role_id)
        if not result["ok"]:
            return result
        status=result.get("status")
        blocked={"REQUIRES_ROLE_BENCH","REQUIRES_VISION_BENCH","REQUIRES_CREATIVE_SEMANTIC_REVIEW"}
        if status in blocked and not allow_unbenchmarked:
            return {**result,"ok":False,"reason":"role_requires_benchmark"}
        return result
