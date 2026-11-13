from dataclasses import replace

from father.knowledge_factory.entity_graph import (
    DeterministicEntityGraphBuilder,
    GraphResolutionPolicy,
)
from father.knowledge_factory.entity_relation import (
    EntityRecord,
    ExtractionSet,
    RelationRecord,
)


def _entity(entity_id, name, entity_type="TERM", evidence=("CHK-1",)):
    return EntityRecord(
        entity_id=entity_id,
        entity_type=entity_type,
        canonical_name=name,
        aliases=(),
        confidence=0.9,
        evidence_chunk_ids=evidence,
        entity_hash=(entity_id[-1] * 64),
    )


def _relation(relation_id, subject, obj, evidence=("CHK-1",)):
    return RelationRecord(
        relation_id=relation_id,
        relation_type="POINTS_TO",
        subject_entity_id=subject,
        object_entity_id=obj,
        confidence=0.95,
        evidence_chunk_ids=evidence,
        relation_hash=(relation_id[-1] * 64),
    )


def _set(set_id, entities, relations=(), hash_char="a"):
    return ExtractionSet(
        extraction_set_id=set_id,
        chunk_set_id=f"CHSET-{set_id}",
        chunk_set_hash=hash_char * 64,
        extractor_id="EXTRACTOR",
        extractor_version="1.0",
        policy_id="POL-E",
        policy_version="1.0",
        entities=tuple(entities),
        relations=tuple(relations),
        extraction_set_hash=hash_char * 64,
    )


def test_exact_same_type_name_merges_and_preserves_lineage():
    a1 = _entity("ENT-A1", "Alpha", evidence=("CHK-1",))
    a2 = _entity("ENT-A2", " alpha ", evidence=("CHK-2",))
    first = _set("EX-1", (a1,), hash_char="a")
    second = _set("EX-2", (a2,), hash_char="b")

    result = DeterministicEntityGraphBuilder().build(
        (first, second),
        GraphResolutionPolicy("POL-G", "1.0"),
    )

    assert result.status == "BUILT"
    assert len(result.graph.nodes) == 1
    node = result.graph.nodes[0]
    assert node.source_entity_ids == ("ENT-A1", "ENT-A2")
    assert node.evidence_chunk_ids == ("CHK-1", "CHK-2")


def test_same_name_different_type_creates_conflict_without_merge():
    first = _set("EX-1", (_entity("ENT-A1", "Alpha", "TERM"),), hash_char="a")
    second = _set("EX-2", (_entity("ENT-A2", "Alpha", "ORG"),), hash_char="b")

    result = DeterministicEntityGraphBuilder().build(
        (first, second),
        GraphResolutionPolicy("POL-G", "1.0"),
    )

    assert result.status == "BUILT"
    assert len(result.graph.nodes) == 2
    assert len(result.graph.conflicts) == 1
    assert result.graph.conflicts[0].conflict_type == "SAME_NAME_DIFFERENT_TYPE"


def test_relations_resolve_and_duplicate_edges_union_lineage():
    a1 = _entity("ENT-A1", "Alpha", evidence=("CHK-1",))
    b1 = _entity("ENT-B1", "Beta", evidence=("CHK-1",))
    r1 = _relation("REL-R1", "ENT-A1", "ENT-B1", evidence=("CHK-1",))
    first = _set("EX-1", (a1, b1), (r1,), hash_char="a")

    a2 = _entity("ENT-A2", "alpha", evidence=("CHK-2",))
    b2 = _entity("ENT-B2", "Beta", evidence=("CHK-2",))
    r2 = _relation("REL-R2", "ENT-A2", "ENT-B2", evidence=("CHK-2",))
    second = _set("EX-2", (a2, b2), (r2,), hash_char="b")

    result = DeterministicEntityGraphBuilder().build(
        (first, second),
        GraphResolutionPolicy("POL-G", "1.0"),
    )

    assert result.status == "BUILT"
    assert len(result.graph.edges) == 1
    edge = result.graph.edges[0]
    assert edge.source_relation_ids == ("REL-R1", "REL-R2")
    assert edge.evidence_chunk_ids == ("CHK-1", "CHK-2")


def test_dangling_relation_is_rejected():
    a = _entity("ENT-A1", "Alpha")
    bad = _relation("REL-R1", "ENT-A1", "ENT-MISSING")
    extraction = _set("EX-1", (a,), (bad,), hash_char="a")

    result = DeterministicEntityGraphBuilder().build(
        (extraction,),
        GraphResolutionPolicy("POL-G", "1.0"),
    )

    assert result.status == "REJECTED"
    assert any("dangling relation object" in item for item in result.diagnostics)


def test_input_order_does_not_change_graph_hash():
    first = _set("EX-1", (_entity("ENT-A1", "Alpha"),), hash_char="a")
    second = _set("EX-2", (_entity("ENT-B1", "Beta"),), hash_char="b")
    builder = DeterministicEntityGraphBuilder()
    policy = GraphResolutionPolicy("POL-G", "1.0")

    forward = builder.build((first, second), policy)
    reverse = builder.build((second, first), policy)

    assert forward.graph.graph_hash == reverse.graph.graph_hash
    assert forward.graph.graph_id == reverse.graph.graph_id


def test_policy_version_changes_identity():
    extraction = _set("EX-1", (_entity("ENT-A1", "Alpha"),), hash_char="a")
    builder = DeterministicEntityGraphBuilder()

    first = builder.build((extraction,), GraphResolutionPolicy("POL-G", "1.0"))
    second = builder.build((extraction,), GraphResolutionPolicy("POL-G", "2.0"))

    assert first.graph.graph_hash != second.graph.graph_hash


def test_no_inferred_edges_are_created():
    extraction = _set(
        "EX-1",
        (_entity("ENT-A1", "Alpha"), _entity("ENT-B1", "Beta")),
        (),
        hash_char="a",
    )
    result = DeterministicEntityGraphBuilder().build(
        (extraction,),
        GraphResolutionPolicy("POL-G", "1.0"),
    )
    assert result.status == "BUILT"
    assert result.graph.edges == ()


def test_invalid_policy_is_rejected():
    extraction = _set("EX-1", (_entity("ENT-A1", "Alpha"),), hash_char="a")
    result = DeterministicEntityGraphBuilder().build(
        (extraction,),
        GraphResolutionPolicy("POL-G", "1.0", exact_name_same_type_merge=False),
    )
    assert result.status == "REJECTED"
