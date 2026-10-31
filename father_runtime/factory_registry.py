from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml


def _load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


@dataclass(frozen=True)
class ModelBindingRequest:
    agent_id: str
    required_capabilities: tuple[str, ...]
    local_only: bool = False
    max_vram_gb: float | None = None
    min_context_window: int | None = None
    security_class: str | None = None


class FactoryRegistry:
    def __init__(
        self,
        repo_root: str | Path=".",
        model_registry: str="factory/registry/MODEL_REGISTRY.yaml",
        agent_registry: str="factory/registry/AGENT_REGISTRY_V1.yaml",
    ) -> None:
        self.repo_root=Path(repo_root)
        self.model_registry_path=self.repo_root/model_registry
        self.agent_registry_path=self.repo_root/agent_registry

    def models(self) -> list[dict[str, Any]]:
        return list(_load(self.model_registry_path).get("models", []))

    def agents(self) -> list[dict[str, Any]]:
        return list(_load(self.agent_registry_path).get("agents", []))

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        return next((a for a in self.agents() if a.get("agent_id")==agent_id), None)

    def compatible_models(self, request: ModelBindingRequest) -> list[dict[str, Any]]:
        result=[]
        for model in self.models():
            caps=model.get("capabilities", {})
            if not all(caps.get(cap) is True for cap in request.required_capabilities):
                continue
            if request.local_only and not model.get("artifact", {}).get("path"):
                continue
            if request.max_vram_gb is not None:
                vram=model.get("resources", {}).get("vram_estimate_gb")
                if vram is not None and float(vram) > request.max_vram_gb:
                    continue
            if request.min_context_window is not None:
                ctx=caps.get("context_window")
                if ctx is not None and int(ctx) < request.min_context_window:
                    continue
            if request.security_class:
                allowed=model.get("lifecycle", {}).get("approved_agent_classes", [])
                if allowed and request.security_class not in allowed:
                    continue
            if model.get("lifecycle", {}).get("state") not in {
                "COMPATIBLE","TESTED","VERIFIED","APPROVED_FOR_AGENT"
            }:
                continue
            result.append(model)
        return result
