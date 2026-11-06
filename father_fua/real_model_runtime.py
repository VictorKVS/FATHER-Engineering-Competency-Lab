from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass
from typing import Callable

from father_fua.audit import AuditLog
from father_fua.context_manager import ContextManager, ContextSegment
from father_fua.evidence import Evidence, create_evidence
from father_fua.local_models import DiscoveredModel, discover_local_models, invoke_model
from father_fua.policy import PolicyEngine
from father_fua.prompt_runtime import assemble_prompt


@dataclass(frozen=True)
class RealModelMissionResult:
    mission_id: str
    model: DiscoveredModel
    response: str
    response_sha256: str
    latency_ms: int
    evidence: Evidence
    audit_ok: bool


class RealModelMissionRuntime:
    def __init__(
        self,
        *,
        discoverer: Callable[[], list[DiscoveredModel]] = discover_local_models,
        invoker: Callable[[DiscoveredModel, str, float], str] = invoke_model,
    ) -> None:
        self.discoverer = discoverer
        self.invoker = invoker
        self.policy = PolicyEngine("0.3")
        self.policy.allow("FUA-001", "model.call")
        self.context = ContextManager()
        self.audit = AuditLog()

    def choose_model(self) -> DiscoveredModel:
        models = [
            m for m in self.discoverer()
            if m.local and m.healthy and m.supports_chat
        ]
        if not models:
            raise LookupError("no healthy local chat model discovered")
        preferred = (
            "qwen2.5:7b",
            "deepseek-r1:7b",
            "qwen2.5:3b",
            "llama3.2:1b",
            "qwen2.5-coder:7b-instruct-q4_K_M",
            "qwen2.5-coder:1.5b",
            "qwen3-vl:8b-instruct-q4_K_M",
            "llava:7b",
        )
        rank = {name: i for i, name in enumerate(preferred)}
        models.sort(key=lambda m: (rank.get(m.model_id, len(rank)), m.model_id.lower()))
        return models[0]

    def run(self, mission: str, *, timeout: float = 300.0) -> RealModelMissionResult:
        if not mission or len(mission) > 10000:
            raise ValueError("invalid mission length")

        mission_id = str(uuid.uuid4())
        model = self.choose_model()

        decision = self.policy.decide(
            subject="FUA-001",
            action="model.call",
            data_classification="INTERNAL",
            target_model_location="LOCAL",
        )
        if decision.decision != "ALLOW":
            raise PermissionError("model call denied")

        segments = self.context.build(
            [
                ContextSegment("policy", "DENY BY DEFAULT", 100, mandatory=True, source="policy"),
                ContextSegment("mission", mission, 90, mandatory=True, source="operator"),
            ],
            max_chars=4096,
            remote_target=False,
        )

        prompt_package = assemble_prompt(
            system=(
                "You are operating inside FATHER FUA-001 test runtime. "
                "Follow the mission only. Do not claim external actions. "
                "Return a concise factual text response."
            ),
            role="ANALYST",
            task=mission,
            context=[],
        )

        prompt = "\n".join(
            str(message["content"])
            for message in prompt_package.messages
            if message["role"] in {"system", "user"}
        )

        self.audit.append(
            kind="real_model.call.started",
            actor="FUA-001",
            correlation_id=mission_id,
            detail={
                "transport": model.transport,
                "model_id": model.model_id,
                "base_url": model.base_url,
                "prompt_sha256": prompt_package.sha256,
                "context_segments": [s.segment_id for s in segments],
            },
        )

        started = time.perf_counter()
        try:
            response = self.invoker(model, prompt, timeout)
        except TimeoutError:
            # First load of a local model can be substantially slower than steady-state.
            # Retry once with a larger bounded timeout rather than classifying cold start as failure.
            response = self.invoker(model, prompt, max(timeout * 2, 600.0))
        latency_ms = int((time.perf_counter() - started) * 1000)

        response_sha = hashlib.sha256(response.encode("utf-8")).hexdigest()
        evidence = create_evidence(
            f"EVID-REALMODEL-{mission_id}",
            "REAL_LOCAL_MODEL_TEST",
            {
                "mission_id": mission_id,
                "transport": model.transport,
                "model_id": model.model_id,
                "base_url": model.base_url,
                "prompt_sha256": prompt_package.sha256,
                "response_sha256": response_sha,
                "response_length": len(response),
                "latency_ms": latency_ms,
            },
        )

        self.audit.append(
            kind="real_model.call.completed",
            actor="FUA-001",
            correlation_id=mission_id,
            detail={
                "response_sha256": response_sha,
                "latency_ms": latency_ms,
                "evidence_id": evidence.evidence_id,
            },
        )

        return RealModelMissionResult(
            mission_id=mission_id,
            model=model,
            response=response,
            response_sha256=response_sha,
            latency_ms=latency_ms,
            evidence=evidence,
            audit_ok=self.audit.verify(),
        )
