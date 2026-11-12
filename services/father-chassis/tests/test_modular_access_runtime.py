import pytest

from father.bootstrap import build_runtime
from father.core.access_control import ClearanceLevel, ResourceContext, SubjectContext
from father.core.contracts import ExecutionRequest


def test_access_denied_before_rag_and_model(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    runtime.rag.ingest("secret://kii", "restricted evidence must never reach unauthorized retrieval")

    subject = SubjectContext(
        subject_id="viewer",
        roles=frozenset({"viewer"}),
        clearance=ClearanceLevel.PUBLIC,
    )
    resource = ResourceContext(
        resource_id="kii-secret",
        classification=ClearanceLevel.RESTRICTED,
        compartments=frozenset({"KII"}),
    )

    with pytest.raises(PermissionError):
        runtime.run(
            ExecutionRequest(
                input="show restricted evidence",
                metadata={
                    "subject_context": subject,
                    "resource_context": resource,
                    "permission": "execute:analysis",
                },
            )
        )

    events = runtime.audit._events
    access_events = [e for e in events if e.type == "access.decision"]
    assert access_events
    assert access_events[-1].payload["allowed"] is False
    assert not any(e.type == "rag.completed" for e in events)
    assert not any(e.type == "model.completed" for e in events)


def test_authorized_analyst_reaches_full_pipeline(tmp_path):
    runtime = build_runtime(data_dir=tmp_path)
    runtime.rag.ingest("internal://kb", "authorized evidence for analyst")

    subject = SubjectContext(
        subject_id="analyst",
        roles=frozenset({"analyst"}),
        clearance=ClearanceLevel.INTERNAL,
        projects=frozenset({"p1"}),
    )
    resource = ResourceContext(
        resource_id="internal-kb",
        classification=ClearanceLevel.INTERNAL,
        project_id="p1",
    )

    result = runtime.run(
        ExecutionRequest(
            input="authorized evidence",
            metadata={
                "subject_context": subject,
                "resource_context": resource,
                "permission": "execute:analysis",
            },
        )
    )

    assert result.output
    assert any(e.type == "access.decision" and e.payload["allowed"] for e in result.events)
    assert any(e.type == "rag.completed" for e in result.events)
    assert any(e.type == "model.completed" for e in result.events)
