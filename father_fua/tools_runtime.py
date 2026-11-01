from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    privileged: bool
    allowed_roles: tuple[str, ...]


class ToolRuntime:
    def __init__(self) -> None:
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, Callable[[dict], Any]] = {}
        self.audit: list[dict] = []

    def register(self, spec: ToolSpec, handler: Callable[[dict], Any]) -> None:
        self._specs[spec.tool_id] = spec
        self._handlers[spec.tool_id] = handler

    def execute(
        self,
        tool_id: str,
        payload: dict,
        *,
        role: str,
        policy_allow: bool,
        human_approved: bool = False,
    ) -> Any:
        spec = self._specs.get(tool_id)
        if spec is None:
            raise PermissionError("unknown tool")
        if not policy_allow:
            raise PermissionError("policy denied")
        if role not in spec.allowed_roles:
            raise PermissionError("role denied")
        if spec.privileged and not human_approved:
            raise PermissionError("human approval required")
        if not isinstance(payload, dict):
            raise ValueError("payload must be object")
        result = self._handlers[tool_id](payload)
        self.audit.append({"tool_id": tool_id, "role": role, "status": "EXECUTED"})
        return result
