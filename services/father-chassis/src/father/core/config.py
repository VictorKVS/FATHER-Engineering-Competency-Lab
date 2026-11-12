from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RetryConfig:
    attempts: int = 2
    timeout_ms: int = 1000


@dataclass(slots=True)
class ChassisConfig:
    name: str = "FATHER_CHASSIS"
    version: str = "0.4.0"
    workflow: str = "default"
    emergency_stop: bool = False
    retry: RetryConfig = field(default_factory=RetryConfig)
    human_approval_for: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class ConfigurationError(ValueError):
    pass


def load_config(path: str | Path) -> ChassisConfig:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    retry = raw.get("retry", {})
    policies = raw.get("policies", {})
    cfg = ChassisConfig(
        name=str(raw.get("name", "FATHER_CHASSIS")),
        version=str(raw.get("version", "0.4.0")),
        workflow=str(raw.get("workflow", "default")),
        emergency_stop=bool(raw.get("emergency_stop", False)),
        retry=RetryConfig(
            attempts=max(1, int(retry.get("attempts", 2))),
            timeout_ms=max(1, int(retry.get("timeout_ms", 1000))),
        ),
        human_approval_for=tuple(str(x) for x in policies.get("human_approval_for", [])),
        metadata=dict(raw.get("metadata", {})),
    )
    if not cfg.name.strip():
        raise ConfigurationError("name must not be empty")
    return cfg
