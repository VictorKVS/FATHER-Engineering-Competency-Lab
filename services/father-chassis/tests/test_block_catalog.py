from father.factory.block_catalog import (
    BlockCatalog,
    BlockDescriptor,
    build_reference_block_catalog,
)


def test_reference_catalog_matches_existing_factory_capabilities():
    catalog = build_reference_block_catalog()
    result = catalog.match({
        "agent.execute",
        "workflow.execute",
        "model.generate",
        "knowledge.retrieve",
        "audit.write",
        "evidence.trace",
        "policy.enforce",
        "report.create",
    })

    assert result.complete is True
    assert result.unresolved_capabilities == ()
    assert "FTH-RUNTIME-AGENT-001" in {b.block_id for b in result.selected_blocks}
    assert "FTH-MODEL-ROUTER-001" in {b.block_id for b in result.selected_blocks}


def test_matcher_is_deterministic_for_equal_coverage():
    catalog = BlockCatalog([
        BlockDescriptor("B-BLOCK", "1.0", "test", frozenset({"x"})),
        BlockDescriptor("A-BLOCK", "1.0", "test", frozenset({"x"})),
    ])

    result = catalog.match({"x"})

    assert result.complete is True
    assert [b.block_id for b in result.selected_blocks] == ["A-BLOCK"]


def test_matcher_preserves_unresolved_capability():
    catalog = build_reference_block_catalog()
    result = catalog.match({"vision.analyze"})

    assert result.complete is False
    assert result.unresolved_capabilities == ("vision.analyze",)
