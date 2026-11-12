from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Capability:
    name: str
    version: str = "1.0"
    provider_kind: str = "internal"
    metadata: dict[str, str] = field(default_factory=dict)


class CapabilityRegistry:
    def __init__(self) -> None:
        self._caps: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        current = self._caps.get(capability.name)
        if current and current.version != capability.version:
            raise ValueError(
                f"capability version conflict for {capability.name}: "
                f"{current.version} != {capability.version}"
            )
        self._caps[capability.name] = capability

    def register_many(self, capabilities: Iterable[Capability]) -> None:
        for capability in capabilities:
            self.register(capability)

    def has(self, name: str) -> bool:
        return name in self._caps

    def require(self, names: Iterable[str]) -> list[str]:
        return sorted(name for name in names if name not in self._caps)

    def list(self) -> list[Capability]:
        return sorted(self._caps.values(), key=lambda c: c.name)
