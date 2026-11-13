import pytest

from father.bootstrap import build_runtime
from father.core.approval import ApprovalRequired
from father.factory.product_runtime import AssembledProductRuntime
from father.factory.reference_products import osint_knowledge_spec, security_kii_spec


def _runtime(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    runtime.rag.ingest(
        "kb://osint",
        "OSINT analysis uses traceable sources, evidence and auditable reporting.",
    )
    runtime.rag.ingest(
        "kb://kii",
        "KII security analysis requires policy enforcement, normative evidence and human validation.",
    )
    return runtime


def test_osint_product_composes_executes_and_qualifies(tmp_path):
    product_runtime = AssembledProductRuntime(_runtime(tmp_path))
    spec = osint_knowledge_spec()

    product, execution, record = product_runtime.execute(
        spec=spec,
        user_input="How does OSINT analysis use evidence?",
    )

    assert product.recipe.product_id == spec.product_id
    assert execution.status == "EXECUTED"
    assert execution.evidence
    assert execution.qualification["qualified"] is True
    assert record.qualified is True
    assert record.recipe_hash == product.recipe.recipe_hash
    assert record.assembly_hash == product.assembly.assembly_hash
    assert record.evidence_hash


def test_security_kii_product_stops_for_approval_then_qualifies(tmp_path):
    runtime = _runtime(tmp_path)
    product_runtime = AssembledProductRuntime(runtime)
    spec = security_kii_spec()

    with pytest.raises(ApprovalRequired) as pending:
        product_runtime.execute(
            spec=spec,
            user_input="What does KII security analysis require?",
        )

    approval = runtime.approval_gate.approve(pending.value.approval_id)
    product, execution, record = product_runtime.execute(
        spec=spec,
        user_input="What does KII security analysis require?",
        approval_id=approval.approval_id,
    )

    assert product.recipe.product_id == spec.product_id
    assert execution.status == "EXECUTED"
    assert execution.qualification["qualified"] is True
    assert record.qualified is True
    assert record.evidence_hash
