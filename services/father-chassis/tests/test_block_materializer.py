from dataclasses import replace
from pathlib import Path

from father.factory.block_materializer import (
    BlockMaterializationRequest,
    QualifiedBlockArtifact,
    QualifiedBlockMaterializer,
    canonical_tree_hash,
)


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "source-block"
    source.mkdir()
    (source / "block.py").write_text("VALUE = 1\n", encoding="utf-8")
    (source / "config.json").write_text('{"enabled":true}\n', encoding="utf-8")
    return source


def _artifact(source: Path, **changes):
    base = QualifiedBlockArtifact(
        block_id="FTH-TEST-BLOCK-001",
        version="1.0.0",
        source_path=str(source),
        canonical_hash=canonical_tree_hash(source),
        qualification_status="QUALIFIED",
        supported_delivery_modes=(
            "EMBEDDED_COPY",
            "PACKAGE_DEPENDENCY",
            "SIDECAR",
            "SHARED_SERVICE",
        ),
        capabilities=("test.capability",),
    )
    return replace(base, **changes)


def _request(tmp_path: Path, artifact, **changes):
    base = BlockMaterializationRequest(
        product_id="AGENT-DEMO",
        product_version="0.1.0",
        workspace_path=str(tmp_path / "workspace"),
        block=artifact,
        delivery_mode="EMBEDDED_COPY",
    )
    return replace(base, **changes)


def test_embedded_copy_verifies_hash(tmp_path):
    source = _source(tmp_path)
    artifact = _artifact(source)
    result = QualifiedBlockMaterializer().materialize(_request(tmp_path, artifact))
    assert result.status == "MATERIALIZED"
    assert result.materialized_path is not None
    assert canonical_tree_hash(Path(result.materialized_path)) == artifact.canonical_hash


def test_unqualified_block_rejected(tmp_path):
    source = _source(tmp_path)
    artifact = _artifact(source, qualification_status="DRAFT")
    result = QualifiedBlockMaterializer().materialize(_request(tmp_path, artifact))
    assert result.status == "REJECTED"


def test_tampered_source_rejected(tmp_path):
    source = _source(tmp_path)
    artifact = _artifact(source)
    (source / "block.py").write_text("VALUE = 2\n", encoding="utf-8")
    result = QualifiedBlockMaterializer().materialize(_request(tmp_path, artifact))
    assert result.status == "REJECTED"
    assert "source hash mismatch" in result.diagnostics


def test_unsupported_delivery_mode_rejected(tmp_path):
    source = _source(tmp_path)
    artifact = _artifact(source, supported_delivery_modes=("EMBEDDED_COPY",))
    request = _request(tmp_path, artifact, delivery_mode="SHARED_SERVICE")
    assert QualifiedBlockMaterializer().materialize(request).status == "REJECTED"


def test_shared_service_creates_binding_without_copy(tmp_path):
    source = _source(tmp_path)
    artifact = _artifact(source)
    request = _request(tmp_path, artifact, delivery_mode="SHARED_SERVICE")
    result = QualifiedBlockMaterializer().materialize(request)
    assert result.status == "BOUND"
    assert result.binding is not None
    assert result.materialized_path is None
    assert not (tmp_path / "workspace" / "blocks").exists()


def test_identical_second_copy_is_deterministic(tmp_path):
    source = _source(tmp_path)
    artifact = _artifact(source)
    request = _request(tmp_path, artifact)
    first = QualifiedBlockMaterializer().materialize(request)
    second = QualifiedBlockMaterializer().materialize(request)
    assert first.status == second.status == "MATERIALIZED"
    assert first.assembly_hash != ""
    assert second.assembly_hash != ""


def test_conflicting_existing_target_rejected(tmp_path):
    source = _source(tmp_path)
    artifact = _artifact(source)
    request = _request(tmp_path, artifact)
    materializer = QualifiedBlockMaterializer()
    first = materializer.materialize(request)
    assert first.status == "MATERIALIZED"
    target = Path(first.materialized_path)
    (target / "block.py").write_text("TAMPERED = True\n", encoding="utf-8")
    second = materializer.materialize(request)
    assert second.status == "REJECTED"


def test_path_unsafe_id_rejected(tmp_path):
    source = _source(tmp_path)
    artifact = _artifact(source, block_id="../bad")
    result = QualifiedBlockMaterializer().materialize(_request(tmp_path, artifact))
    assert result.status == "REJECTED"
