from __future__ import annotations
from dataclasses import dataclass, asdict
from father.core.contracts import ExecutionRequest

@dataclass
class KnowledgeQualificationResult:
    ingest_chunks: int
    trace_id: str
    evidence_count: int
    output_nonempty: bool
    audit_event_count: int
    passed: bool

    def to_dict(self):
        return asdict(self)

def qualify_knowledge_flow(runtime, *, source: str, text: str, question: str) -> KnowledgeQualificationResult:
    ingest = getattr(runtime.rag, "ingest", None)
    if not callable(ingest):
        raise RuntimeError("RAG adapter does not support ingestion")
    chunks = int(ingest(source, text))
    result = runtime.run(ExecutionRequest(input=question))
    audit = runtime.audit.by_trace(result.trace.trace_id)
    passed = (
        chunks > 0
        and len(result.evidence) > 0
        and bool(str(result.output).strip())
        and len(audit) >= 2
    )
    return KnowledgeQualificationResult(
        ingest_chunks=chunks,
        trace_id=result.trace.trace_id,
        evidence_count=len(result.evidence),
        output_nonempty=bool(str(result.output).strip()),
        audit_event_count=len(audit),
        passed=passed,
    )
