from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProfile:
    model_id: str
    provider: str
    local_or_remote: str
    context_window: int
    structured_output: bool
    tool_calling: bool
    cost_profile: float
    privacy_profile: str
    healthy: bool
    approved: bool = True


class ModelRouter:
    def __init__(self) -> None:
        self._models: list[ModelProfile] = []

    def register(self, profile: ModelProfile) -> None:
        self._models.append(profile)

    def select(
        self,
        *,
        min_context: int = 0,
        require_tools: bool = False,
        require_structured: bool = False,
        local_only: bool = False,
        max_cost: float | None = None,
    ) -> ModelProfile:
        candidates = []
        for m in self._models:
            if not m.approved or not m.healthy:
                continue
            if m.context_window < min_context:
                continue
            if require_tools and not m.tool_calling:
                continue
            if require_structured and not m.structured_output:
                continue
            if local_only and m.local_or_remote != "LOCAL":
                continue
            if max_cost is not None and m.cost_profile > max_cost:
                continue
            candidates.append(m)
        if not candidates:
            raise LookupError("no approved compatible model")
        candidates.sort(key=lambda m: (m.cost_profile, -m.context_window))
        return candidates[0]
