from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SandboxPolicy:
    network_allowed: bool = False
    max_seconds: int = 30
    allowed_roots: tuple[str, ...] = ()


def validate_path(path: str, policy: SandboxPolicy) -> bool:
    normalized = path.replace("\\","/").lower()
    return any(normalized.startswith(root.replace("\\","/").lower()) for root in policy.allowed_roots)
