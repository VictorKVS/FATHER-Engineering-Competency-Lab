from pathlib import Path

import pytest

from father.bootstrap import build_runtime
from father.core.contracts import ExecutionRequest


def test_modular_runtime_end_to_end(tmp_path: Path):
    runtime = build_runtime(data_dir=tmp_path)
    runtime.rag.ingest(
        "qualification://modular-core",
        "FATHER modular core provides workflow, routing, RAG, evidence, audit, policy and tools.",
    )

    result = runtime.run(
        ExecutionRequest(
            input="What capabilities does the FATHER modular core provide?",
            metadata={"role": "agent"},
        )
    )

    assert result.output
    assert result.trace.trace_id
    assert result.evidence
    assert len(runtime.audit.by_trace(result.trace.trace_id)) >= 6
    assert runtime.state.get("workflow", result.trace.workflow_id)["status"] == "completed"
    assert runtime.metrics.counters["requests_success"] == 1
    assert runtime.tracer.by_trace(result.trace.trace_id)


def test_modular_runtime_emergency_stop(tmp_path: Path):
    runtime = build_runtime(data_dir=tmp_path)
    runtime.emergency_stop.engage()

    with pytest.raises(RuntimeError, match="emergency stop"):
        runtime.run(ExecutionRequest(input="must be blocked"))

    runtime.emergency_stop.release()
    runtime.rag.ingest("qualification://resume", "FATHER resumes after emergency stop release.")
    result = runtime.run(ExecutionRequest(input="Does FATHER resume?"))
    assert result.output


def test_registry_contains_standard_blocks(tmp_path: Path):
    runtime = build_runtime(data_dir=tmp_path)
    block_ids = {b.block_id for b in runtime.registry.list()}

    assert "FTH-RAG-SQLITE-001" in block_ids
    assert "FTH-MODEL-001" in block_ids
    assert "FTH-TOOL-001" in block_ids
    assert "FTH-GUARD-001" in block_ids
    assert "FTH-STATE-SQLITE-001" in block_ids
