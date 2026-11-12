from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable

from father.core.contracts import ExecutionRequest

@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_type: str
    title: str
    content: str
    uri: str | None = None
    collected_at: str | None = None

    def normalized(self) -> "SourceRecord":
        text = " ".join(self.content.split())
        collected = self.collected_at or datetime.now(timezone.utc).isoformat()
        sid = self.source_id or sha256(
            f"{self.source_type}|{self.title}|{self.uri}|{text}".encode("utf-8")
        ).hexdigest()[:16]
        return SourceRecord(
            source_id=sid,
            source_type=self.source_type.strip().lower(),
            title=self.title.strip(),
            content=text,
            uri=self.uri,
            collected_at=collected,
        )

@dataclass
class OSINTReport:
    product_id: str
    query: str
    trace_id: str
    answer: str
    evidence_count: int
    source_ids: list[str]
    sources: list[dict]
    claims: list[dict]
    status: str

    def to_dict(self) -> dict:
        return asdict(self)

class OSINTKnowledgeProduct:
    PRODUCT_ID = "FTH-PRODUCT-OSINT-KNOWLEDGE-001"

    def __init__(self, runtime):
        self.runtime = runtime

    def ingest_sources(self, sources: Iterable[SourceRecord]) -> dict:
        ingest = getattr(self.runtime.rag, "ingest", None)
        if not callable(ingest):
            raise RuntimeError("configured RAG adapter does not support ingestion")
        accepted = 0
        chunks = 0
        reused_sources = 0
        normalized_sources = []
        for raw in sources:
            src = raw.normalized()
            if not src.content:
                continue
            payload = (
                f"[SOURCE_ID={src.source_id}] "
                f"[TYPE={src.source_type}] "
                f"[TITLE={src.title}] "
                f"[URI={src.uri or ''}] "
                f"{src.content}"
            )
            inserted = int(ingest(src.source_id, payload))
            chunks += inserted
            if inserted == 0:
                reused_sources += 1
            accepted += 1
            normalized_sources.append(src)
        return {
            "accepted_sources": accepted,
            "chunks": chunks,
            "reused_sources": reused_sources,
            "ingest_status": (
                "EMPTY"
                if accepted == 0
                else ("REUSED" if chunks == 0 else ("MIXED" if reused_sources else "INSERTED"))
            ),
            "sources": [asdict(s) for s in normalized_sources],
        }

    def investigate(self, query: str, *, source_manifest: list[dict] | None = None) -> OSINTReport:
        result = self.runtime.run(ExecutionRequest(input=query))
        evidence = list(result.evidence or [])
        source_ids = []
        for ev in evidence:
            text = str(ev)
            marker = "[SOURCE_ID="
            if marker in text:
                sid = text.split(marker, 1)[1].split("]", 1)[0]
                if sid and sid not in source_ids:
                    source_ids.append(sid)

        claims = [{
            "claim": str(result.output),
            "status": "SUPPORTED" if evidence else "UNVERIFIED",
            "evidence_count": len(evidence),
            "source_ids": source_ids,
        }]

        return OSINTReport(
            product_id=self.PRODUCT_ID,
            query=query,
            trace_id=result.trace.trace_id,
            answer=str(result.output),
            evidence_count=len(evidence),
            source_ids=source_ids,
            sources=source_manifest or [],
            claims=claims,
            status="PASS" if evidence and str(result.output).strip() else "FAIL",
        )

    def full_workflow(self, sources: Iterable[SourceRecord], query: str) -> dict:
        ingest_result = self.ingest_sources(sources)
        report = self.investigate(query, source_manifest=ingest_result["sources"])
        audit = self.runtime.audit.by_trace(report.trace_id)
        return {
            "product_id": self.PRODUCT_ID,
            "ingestion": ingest_result,
            "report": report.to_dict(),
            "audit_event_count": len(audit),
            "passed": (
                ingest_result["accepted_sources"] > 0
                and report.status == "PASS"
                and report.evidence_count > 0
                and len(audit) >= 2
            ),
        }
