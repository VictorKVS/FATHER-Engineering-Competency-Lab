from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    provider_id: str
    provider_kind: str
    version: str
    capabilities: frozenset[str]
    status: str = "AVAILABLE"


class Provider(Protocol):
    descriptor: ProviderDescriptor
    def health(self) -> bool: ...


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        pid = provider.descriptor.provider_id
        if pid in self._providers:
            raise ValueError(f"duplicate provider: {pid}")
        self._providers[pid] = provider

    def resolve(self, *, kind: str, capability: str) -> Provider:
        candidates = [
            p for p in self._providers.values()
            if p.descriptor.provider_kind == kind
            and capability in p.descriptor.capabilities
            and p.descriptor.status == "AVAILABLE"
            and bool(p.health())
        ]
        if not candidates:
            raise LookupError(f"no healthy provider for kind={kind} capability={capability}")
        return sorted(candidates, key=lambda p: p.descriptor.provider_id)[0]

    def list(self) -> list[ProviderDescriptor]:
        return [p.descriptor for p in self._providers.values()]
