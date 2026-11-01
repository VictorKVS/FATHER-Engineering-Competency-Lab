from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    privileged: bool
    allowed_roles: tuple[str, ...]
    max_calls: int = 100


class ToolRuntime:
    def __init__(self) -> None:
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, Callable[[dict], Any]] = {}
        self._calls: dict[str, int] = {}
        self.audit: list[dict] = []

    def register(self, spec: ToolSpec, handler: Callable[[dict], Any]) -> None:
        if spec.max_calls <= 0:
            raise ValueError("max_calls must be positive")
        self._specs[spec.tool_id] = spec
        self._handlers[spec.tool_id] = handler
        self._calls.setdefault(spec.tool_id, 0)

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

        count = self._calls.get(tool_id, 0)
        if count >= spec.max_calls:
            self.audit.append({"tool_id": tool_id, "role": role, "status": "RATE_LIMITED"})
            raise RuntimeError("tool rate limit exceeded")

        result = self._handlers[tool_id](payload)
        self._calls[tool_id] = count + 1
        self.audit.append({"tool_id": tool_id, "role": role, "status": "EXECUTED"})
        return result

    def calls_used(self, tool_id: str) -> int:
        return self._calls.get(tool_id, 0)
