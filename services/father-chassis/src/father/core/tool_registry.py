from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from .contracts import TraceContext


@dataclass(frozen=True, slots=True)
class ActionSchema:
    required: frozenset[str] = field(default_factory=frozenset)
    allowed: frozenset[str] = field(default_factory=frozenset)

    def validate(self, payload: dict[str, Any]) -> None:
        missing = self.required - payload.keys()
        if missing:
            raise ValueError("missing tool payload fields: " + ",".join(sorted(missing)))
        if self.allowed:
            unknown = payload.keys() - self.allowed
            if unknown:
                raise ValueError("unknown tool payload fields: " + ",".join(sorted(unknown)))


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    instance: Any
    actions: frozenset[str]
    roles: frozenset[str] = frozenset({"agent"})
    schemas: dict[str, ActionSchema] = field(default_factory=dict)


class ToolRegistry:
    def __init__(self) -> None: self._tools: dict[str, ToolSpec] = {}
    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools: raise ValueError(f"duplicate tool: {spec.name}")
        self._tools[spec.name] = spec
    def execute(self, name: str, action: str, payload: dict, trace: TraceContext, *, role: str = "agent") -> dict:
        if name not in self._tools: raise KeyError(f"unknown tool: {name}")
        spec = self._tools[name]
        if action not in spec.actions: raise PermissionError(f"tool {name} does not allow action {action}")
        if role not in spec.roles: raise PermissionError(f"role {role} is not allowed for tool {name}")
        schema = spec.schemas.get(action)
        if schema: schema.validate(payload)
        return spec.instance.execute(action, payload, trace)
    def health(self) -> dict[str,bool]:
        return {n: bool(getattr(s.instance,"health",lambda:True)()) for n,s in self._tools.items()}
