from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import load_text, load_yaml, sha256_text


class ContextBuilder:
    """Builds explicit agent context. No hidden conversational state is allowed."""

    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root)

    def _read_ref(self, ref: str | None) -> str:
        if not ref:
            return ""
        p = self.repo_root / ref
        return load_text(p) if p.exists() else ""

    def build(self, stage: dict[str, Any], input_payload: dict[str, Any]) -> dict[str, Any]:
        spec = stage.get("stage", stage)
        intelligence = spec.get("intelligence", {})

        prompt = self._read_ref(intelligence.get("prompt"))
        algorithm = self._read_ref(intelligence.get("algorithm"))
        knowledge = self._read_ref(intelligence.get("knowledge_base"))

        rag_ref = intelligence.get("rag")
        rag_manifest = load_yaml(self.repo_root / rag_ref) if rag_ref and (self.repo_root / rag_ref).exists() else {}

        bundle = {
            "stage": {
                "id": spec.get("id"),
                "name": spec.get("name"),
                "purpose": spec.get("purpose"),
                "processing": spec.get("processing", []),
                "output": spec.get("output", {}),
                "decision": spec.get("decision", {}),
            },
            "prompt": prompt,
            "algorithm": algorithm,
            "rag_manifest": rag_manifest,
            "knowledge_base": knowledge,
            "input": input_payload,
        }
        bundle["hashes"] = {
            "prompt_sha256": sha256_text(prompt),
            "algorithm_sha256": sha256_text(algorithm),
            "knowledge_sha256": sha256_text(knowledge),
        }
        return bundle
