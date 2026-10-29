from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml


class NamingRegistry:
    def __init__(self, root: str | Path = "."):
        self.root = Path(root)
        self.path = self.root / "factory" / "naming" / "NAMING_REGISTRY.yaml"
        self.data = yaml.safe_load(self.path.read_text(encoding="utf-8"))["registry"]
        self.entities = {e["stable_id"]: e for e in self.data["entities"]}

    def get(self, stable_id: str) -> dict[str, Any]:
        return self.entities[stable_id]

    def public_name(self, stable_id: str) -> str:
        return self.get(stable_id)["public_name"]

    def aliases(self, stable_id: str) -> list[str]:
        e = self.get(stable_id)
        values = [e.get("public_name"), e.get("code_name")]
        values += e.get("previous_names", [])
        values += e.get("aliases", [])
        return [x for x in values if x]

    def references(self, stable_id: str) -> list[str]:
        return list(self.get(stable_id).get("references", []))

    def rename_impact(self, stable_id: str, new_public_name: str) -> dict[str, Any]:
        e = self.get(stable_id)
        return {
            "stable_id": stable_id,
            "entity_type": e["entity_type"],
            "current_public_name": e["public_name"],
            "new_public_name": new_public_name,
            "code_name": e.get("code_name"),
            "references_to_review": self.references(stable_id),
            "aliases_to_preserve": self.aliases(stable_id),
            "policy": e.get("rename_policy", "REVIEW"),
        }
