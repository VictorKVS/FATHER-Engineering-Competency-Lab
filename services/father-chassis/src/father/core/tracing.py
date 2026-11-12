from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any


@dataclass(slots=True)
class Span:
    name: str
    trace_id: str
    attributes: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    status: str = "UNSET"


class Tracer:
    """Small OpenTelemetry-compatible-shaped reference tracer.

    It intentionally has no external dependency. Production adapters can export the
    collected spans to OpenTelemetry SDK/collector without changing the runtime contract.
    """
    def __init__(self) -> None:
        self.spans: list[Span] = []

    def record(self, name: str, trace_id: str, fn, **attributes):
        started = perf_counter()
        span = Span(name=name, trace_id=trace_id, attributes=dict(attributes))
        try:
            value = fn()
            span.status = "OK"
            return value
        except Exception as exc:
            span.status = "ERROR"
            span.attributes["error.type"] = type(exc).__name__
            raise
        finally:
            span.duration_ms = (perf_counter() - started) * 1000
            self.spans.append(span)

    def by_trace(self, trace_id: str) -> list[Span]:
        return [s for s in self.spans if s.trace_id == trace_id]
