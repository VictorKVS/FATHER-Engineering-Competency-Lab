from __future__ import annotations

from time import sleep

from father.core.contracts import TraceContext


class MockRag:
    name = "mock-rag-v2"
    def __init__(self, *, fail_times: int = 0, delay_s: float = 0.0) -> None:
        self.fail_times = fail_times
        self.delay_s = delay_s
        self.calls = 0

    def health(self) -> bool:
        return True

    def retrieve(self, query: str, trace: TraceContext) -> list[dict]:
        del query, trace
        self.calls += 1
        if self.delay_s:
            sleep(self.delay_s)
        if self.calls <= self.fail_times:
            raise RuntimeError("transient rag failure")
        return [{"source": "kb://father/chassis", "text": "FATHER uses standard contracts and full traceability.", "score": 1.0}]


class MockModel:
    name = "mock-model-v2"
    def __init__(self, *, label: str = "primary", fail_times: int = 0, delay_s: float = 0.0) -> None:
        self.label = label
        self.name = f"mock-model-v2:{label}"
        self.fail_times = fail_times
        self.delay_s = delay_s
        self.calls = 0

    def health(self) -> bool:
        return True

    def generate(self, prompt: str, trace: TraceContext) -> str:
        del prompt, trace
        self.calls += 1
        if self.delay_s:
            sleep(self.delay_s)
        if self.calls <= self.fail_times:
            raise RuntimeError("transient model failure")
        return f"FATHER Chassis 0.2 processed the request via {self.label} model."


class MockTool:
    name = "mock-tool-v2"
    def __init__(self, *, fail_times: int = 0) -> None:
        self.fail_times = fail_times
        self.calls = 0

    def health(self) -> bool:
        return True

    def execute(self, action: str, payload: dict, trace: TraceContext) -> dict:
        del trace
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError("transient tool failure")
        if action != "create_report":
            raise ValueError(f"unsupported action: {action}")
        return {"output": payload["draft"]}


class DefaultGuardrail:
    name = "default-guardrail-v2"
    def __init__(self, denied_actions: set[str] | None = None) -> None:
        self.denied_actions = denied_actions or set()

    def health(self) -> bool:
        return True

    def allow(self, action: str, payload: dict, trace: TraceContext) -> tuple[bool, str]:
        del payload, trace
        if action in self.denied_actions:
            return False, f"action {action} denied by policy"
        return True, "allowed"
