from father.core.agent_manifest import AgentManifest
from father.core.capabilities import Capability, CapabilityRegistry
from father.core.providers import ProviderDescriptor, ProviderRegistry


class DemoProvider:
    def __init__(self):
        self.descriptor = ProviderDescriptor(
            provider_id="demo-model",
            provider_kind="model",
            version="1.0",
            capabilities=frozenset({"model.generate"}),
        )

    def health(self) -> bool:
        return True


def test_manifest_validates_against_capability_registry():
    registry = CapabilityRegistry()
    registry.register_many([
        Capability("document.read"),
        Capability("report.create"),
        Capability("model.generate", provider_kind="model"),
    ])

    manifest = AgentManifest(
        agent_id="document-analyst",
        version="0.1.0",
        capabilities=frozenset({"document.read", "report.create", "model.generate"}),
        required_permissions=frozenset({"read:evidence"}),
    )

    assert manifest.validate(registry) == []


def test_manifest_reports_missing_capability():
    registry = CapabilityRegistry()
    registry.register(Capability("document.read"))

    manifest = AgentManifest(
        agent_id="future-agent",
        version="0.1.0",
        capabilities=frozenset({"document.read", "vision.analyze"}),
    )

    assert manifest.validate(registry) == ["missing capabilities: vision.analyze"]


def test_provider_registry_resolves_by_kind_and_capability():
    providers = ProviderRegistry()
    providers.register(DemoProvider())

    resolved = providers.resolve(kind="model", capability="model.generate")
    assert resolved.descriptor.provider_id == "demo-model"
