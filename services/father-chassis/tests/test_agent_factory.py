import pytest

from father.bootstrap import build_runtime
from father.core.agent_manifest import AgentManifest
from father.factory.agent_factory import AgentFactory
from father.factory.reference_catalog import (
    build_reference_capabilities,
    build_reference_providers,
)


def test_agent_factory_builds_reference_agent(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    factory = AgentFactory(
        build_reference_capabilities(),
        build_reference_providers(runtime),
    )

    manifest = AgentManifest(
        agent_id="knowledge-analyst",
        version="0.1.0",
        capabilities=frozenset({
            "agent.execute",
            "workflow.execute",
            "knowledge.retrieve",
            "model.generate",
            "report.create",
            "evidence.trace",
            "audit.write",
            "policy.enforce",
        }),
        required_permissions=frozenset({"execute:analysis", "read:evidence"}),
        max_steps=8,
        timeout_seconds=90,
        max_cost_usd=0.25,
    )

    profile = factory.build(manifest)

    assert profile.agent_id == "knowledge-analyst"
    assert profile.build_plan.buildable is True
    bound = {x.capability: x.provider_id for x in profile.build_plan.provider_bindings}
    assert bound["model.generate"] == "runtime-model-router"
    assert bound["knowledge.retrieve"] == "runtime-rag"


def test_agent_factory_rejects_missing_capability(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    factory = AgentFactory(
        build_reference_capabilities(),
        build_reference_providers(runtime),
    )

    manifest = AgentManifest(
        agent_id="vision-agent",
        version="0.1.0",
        capabilities=frozenset({"vision.analyze"}),
    )

    plan = factory.plan(manifest)
    assert plan.buildable is False
    assert any("missing capabilities: vision.analyze" in e for e in plan.errors)

    with pytest.raises(ValueError):
        factory.build(manifest)


def test_agent_factory_rejects_unbound_required_provider(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    factory = AgentFactory(
        build_reference_capabilities(),
        build_reference_providers(runtime),
    )

    manifest = AgentManifest(
        agent_id="strict-agent",
        version="0.1.0",
        capabilities=frozenset({"model.generate"}),
        required_providers=frozenset({"future-vllm-provider"}),
    )

    plan = factory.plan(manifest)
    assert plan.buildable is False
    assert "required provider not bound: future-vllm-provider" in plan.errors
