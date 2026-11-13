from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DomainPack:
    domain_pack_id: str
    version: str
    domain: str
    capabilities: frozenset[str] = frozenset()
    knowledge_sources: tuple[str, ...] = ()
    policies: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.domain_pack_id.strip():
            errors.append("domain_pack_id is required")
        if not self.version.strip():
            errors.append("version is required")
        if not self.domain.strip():
            errors.append("domain is required")
        return errors
