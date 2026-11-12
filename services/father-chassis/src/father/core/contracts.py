from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class TraceContext:
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    request_id: str = field(default_factory=lambda: str(uuid4()))
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    agent_id: str = "father-core-agent"


@dataclass(slots=True)
class Event:
    type: str
    trace_id: str
    payload: dict[str, Any]
    ts: str = field(default_factory=utcnow)


@dataclass(slots=True)
class ExecutionRequest:
    input: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionResult:
    output: str
    trace: TraceContext
    evidence: list[dict[str, Any]]
    events: list[Event]


class ModelAdapter(Protocol):
    name: str
    def generate(self, prompt: str, trace: TraceContext) -> str: ...


class RagAdapter(Protocol):
    name: str
    def retrieve(self, query: str, trace: TraceContext) -> list[dict[str, Any]]: ...


class ToolAdapter(Protocol):
    name: str
    def execute(self, action: str, payload: dict[str, Any], trace: TraceContext) -> dict[str, Any]: ...


class Guardrail(Protocol):
    name: str
    def allow(self, action: str, payload: dict[str, Any], trace: TraceContext) -> tuple[bool, str]: ...
