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
        if not spec.tool_id:
            raise ValueError("tool_id must be non-empty")
        if spec.max_calls <= 0:
            raise ValueError("max_calls must be positive")
        if not spec.allowed_roles:
            raise ValueError("allowed_roles must be non-empty")
        self._specs[spec.tool_id] = spec
        self._handlers[spec.tool_id] = handler
        self._calls.setdefault(spec.tool_id, 0)

    def _record(self, tool_id: str, role: str, status: str, **extra: Any) -> None:
        event={"tool_id":tool_id,"role":role,"status":status}
        event.update(extra)
        self.audit.append(event)

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
            self._record(tool_id,role,"DENIED",reason="UNKNOWN_TOOL")
            raise PermissionError("unknown tool")
        if not policy_allow:
            self._record(tool_id,role,"DENIED",reason="POLICY")
            raise PermissionError("policy denied")
        if role not in spec.allowed_roles:
            self._record(tool_id,role,"DENIED",reason="ROLE")
            raise PermissionError("role denied")
        if spec.privileged and not human_approved:
            self._record(tool_id,role,"DENIED",reason="HUMAN_APPROVAL")
            raise PermissionError("human approval required")
        if not isinstance(payload, dict):
            self._record(tool_id,role,"REJECTED",reason="INVALID_PAYLOAD")
            raise ValueError("payload must be object")

        count = self._calls.get(tool_id, 0)
        if count >= spec.max_calls:
            self._record(tool_id,role,"RATE_LIMITED")
            raise RuntimeError("tool rate limit exceeded")

        try:
            result = self._handlers[tool_id](payload)
        except Exception as exc:
            self._record(tool_id,role,"FAILED",error_type=type(exc).__name__)
            raise

        self._calls[tool_id] = count + 1
        self._record(tool_id,role,"EXECUTED")
        return result

    def reset_call_budget(self, tool_id: str | None = None) -> None:
        """Reset per-scope tool call counters without altering registrations or audit history."""
        if tool_id is None:
            for registered in self._specs:
                self._calls[registered] = 0
            return
        if tool_id not in self._specs:
            raise KeyError(tool_id)
        self._calls[tool_id] = 0

    def calls_used(self, tool_id: str) -> int:
        return self._calls.get(tool_id, 0)
