from __future__ import annotations

from dataclasses import dataclass

from .control import EmergencyStop
from .registry import BlockRegistry


@dataclass(frozen=True, slots=True)
class HealthReport:
    live: bool
    ready: bool
    blocks: dict[str, bool]
    emergency_stop: bool


def health_report(registry: BlockRegistry, stop: EmergencyStop) -> HealthReport:
    blocks = registry.health()
    return HealthReport(
        live=True,
        ready=all(blocks.values()) and not stop.engaged,
        blocks=blocks,
        emergency_stop=stop.engaged,
    )
