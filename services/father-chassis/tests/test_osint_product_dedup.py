from father.bootstrap import build_runtime
from father.products.osint_knowledge import OSINTKnowledgeProduct, SourceRecord


def test_osint_product_reuses_existing_source_without_failing(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    product = OSINTKnowledgeProduct(runtime)

    source = SourceRecord(
        source_id="src-001",
        source_type="document",
        title="Duplicate-safe source",
        content="FATHER modular architecture separates runtime, state, workflow and evidence.",
        uri="local://src-001",
    )

    first = product.full_workflow([source], "What does the source say about FATHER?")
    second = product.full_workflow([source], "What does the source say about FATHER?")

    assert first["passed"] is True
    assert first["ingestion"]["chunks"] > 0
    assert first["ingestion"]["ingest_status"] == "INSERTED"

    assert second["passed"] is True
    assert second["ingestion"]["chunks"] == 0
    assert second["ingestion"]["reused_sources"] == 1
    assert second["ingestion"]["ingest_status"] == "REUSED"
    assert second["report"]["evidence_count"] > 0
