from __future__ import annotations

from dataclasses import dataclass, field

from .capabilities import CapabilityRegistry


@dataclass(frozen=True, slots=True)
class AgentManifest:
    agent_id: str
    version: str
    capabilities: frozenset[str]
    required_permissions: frozenset[str] = frozenset()
    required_providers: frozenset[str] = frozenset()
    max_steps: int = 12
    timeout_seconds: int = 120
    max_cost_usd: float | None = None
    approval_required_for: frozenset[str] = frozenset()
    metadata: dict[str, str] = field(default_factory=dict)

    def validate(self, registry: CapabilityRegistry) -> list[str]:
        errors: list[str] = []
        if not self.agent_id.strip():
            errors.append("agent_id is required")
        if not self.version.strip():
            errors.append("version is required")
        if self.max_steps < 1:
            errors.append("max_steps must be >= 1")
        if self.timeout_seconds < 1:
            errors.append("timeout_seconds must be >= 1")
        missing = registry.require(self.capabilities)
        if missing:
            errors.append("missing capabilities: " + ",".join(missing))
        return errors
