from __future__ import annotations

from father.core.capabilities import Capability, CapabilityRegistry
from father.core.providers import ProviderDescriptor, ProviderRegistry


class RuntimeModelProvider:
    def __init__(self, runtime) -> None:
        self.runtime = runtime
        self.descriptor = ProviderDescriptor(
            provider_id="runtime-model-router",
            provider_kind="model",
            version="1.0",
            capabilities=frozenset({"model.generate"}),
        )

    def health(self) -> bool:
        try:
            self.runtime.models.resolve()
            return True
        except Exception:
            return False


class RuntimeRetrievalProvider:
    def __init__(self, runtime) -> None:
        self.runtime = runtime
        self.descriptor = ProviderDescriptor(
            provider_id="runtime-rag",
            provider_kind="retrieval",
            version="1.0",
            capabilities=frozenset({"knowledge.retrieve"}),
        )

    def health(self) -> bool:
        checker = getattr(self.runtime.rag, "health", None)
        return bool(checker()) if callable(checker) else True


def build_reference_capabilities() -> CapabilityRegistry:
    registry = CapabilityRegistry()
    registry.register_many([
        Capability("agent.execute"),
        Capability("workflow.execute"),
        Capability("report.create"),
        Capability("evidence.trace"),
        Capability("audit.write"),
        Capability("policy.enforce"),
        Capability("decision.trace"),
        Capability("model.generate", provider_kind="model"),
        Capability("knowledge.retrieve", provider_kind="retrieval"),
    ])
    return registry


def build_reference_providers(runtime) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(RuntimeModelProvider(runtime))
    registry.register(RuntimeRetrievalProvider(runtime))
    return registry
