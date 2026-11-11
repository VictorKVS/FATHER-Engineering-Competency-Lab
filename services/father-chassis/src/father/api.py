from __future__ import annotations

import json
import os
import sqlite3
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


VERSION = "1.0.0rc1"
PRODUCT_ID = "FTH-PRODUCT-OSINT-KNOWLEDGE-001"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunBody(BaseModel):
    input: str = Field(min_length=1)
    model: str | None = None
    role: str = "agent"
    approval_id: str | None = None


class IngestBody(BaseModel):
    source: str = Field(min_length=1)
    text: str = Field(min_length=1)


class OSINTSourceBody(BaseModel):
    source_id: str = ""
    source_type: str = "text"
    title: str
    content: str
    uri: str | None = None


class OSINTWorkflowBody(BaseModel):
    query: str = Field(min_length=1)
    sources: list[OSINTSourceBody]


class Runtime:
    """RC recovery runtime.

    This keeps the production HTTP contracts alive while the modular package tree is
    synchronized into GitHub. Storage and audit are persistent SQLite so restart
    qualification remains meaningful.
    """

    def __init__(self) -> None:
        data_dir = Path(os.getenv("FATHER_DATA_DIR", "./data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = data_dir / "father_rc.db"
        self.lock = RLock()
        self.emergency_stop = False
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS knowledge("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "source TEXT NOT NULL,"
                "text TEXT NOT NULL,"
                "created_at TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS audit("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "trace_id TEXT NOT NULL,"
                "type TEXT NOT NULL,"
                "ts TEXT NOT NULL,"
                "payload TEXT NOT NULL)"
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_audit_trace ON audit(trace_id,id)")

    def health(self) -> bool:
        try:
            with self._connect() as db:
                db.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def audit(self, trace_id: str, event_type: str, payload: dict) -> None:
        with self.lock, self._connect() as db:
            db.execute(
                "INSERT INTO audit(trace_id,type,ts,payload) VALUES(?,?,?,?)",
                (trace_id, event_type, utcnow(), json.dumps(payload, ensure_ascii=False)),
            )

    def audit_by_trace(self, trace_id: str) -> list[dict]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT type,ts,payload FROM audit WHERE trace_id=? ORDER BY id",
                (trace_id,),
            ).fetchall()
        return [
            {"type": t, "ts": ts, "payload": json.loads(payload)}
            for t, ts, payload in rows
        ]

    def ingest(self, source: str, text: str, chunk_chars: int = 700) -> int:
        chunks = [
            text[i:i + chunk_chars].strip()
            for i in range(0, len(text), chunk_chars)
            if text[i:i + chunk_chars].strip()
        ]
        with self.lock, self._connect() as db:
            for chunk in chunks:
                db.execute(
                    "INSERT INTO knowledge(source,text,created_at) VALUES(?,?,?)",
                    (source, chunk, utcnow()),
                )
        return len(chunks)

    def retrieve(self, query: str, limit: int = 5) -> list[dict]:
        terms = {x.lower() for x in query.replace("?", " ").replace(",", " ").split() if len(x) > 2}
        with self._connect() as db:
            rows = db.execute(
                "SELECT id,source,text FROM knowledge ORDER BY id DESC LIMIT 500"
            ).fetchall()
        scored = []
        for row_id, source, text in rows:
            lower = text.lower()
            score = sum(1 for term in terms if term in lower)
            if score or not terms:
                scored.append((score, row_id, source, text))
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return [
            {"chunk_id": row_id, "source": source, "text": text, "score": float(score)}
            for score, row_id, source, text in scored[:limit]
        ]

    def run(self, query: str) -> dict:
        if self.emergency_stop:
            raise RuntimeError("FATHER emergency stop is engaged")
        trace_id = str(uuid4())
        self.audit(trace_id, "request.received", {"input": query})
        evidence = self.retrieve(query)
        if evidence:
            snippets = " ".join(item["text"] for item in evidence[:3])
            output = f"Grounded FATHER response: {snippets[:1800]}"
        else:
            output = "UNVERIFIED: no supporting evidence found."
        self.audit(
            trace_id,
            "request.completed",
            {"evidence_count": len(evidence), "output": output},
        )
        return {
            "output": output,
            "trace_id": trace_id,
            "workflow_id": str(uuid4()),
            "evidence": evidence,
            "events": self.audit_by_trace(trace_id),
        }



def call_local_llm(prompt: str) -> dict:
    base_url = os.getenv("FATHER_MODEL_BASE_URL", "").strip()
    model = os.getenv("FATHER_MODEL_NAME", "").strip()
    api_key = os.getenv("FATHER_MODEL_API_KEY", "").strip()

    if not base_url or not model:
        raise RuntimeError("Local LLM is not configured")

    payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are the FATHER qualification model. "
                    "Answer only from the supplied evidence. "
                    "If evidence is insufficient, say UNVERIFIED."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "stream": False,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=payload,
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        body = json.loads(response.read().decode("utf-8"))

    choices = body.get("choices", [])
    if not choices:
        raise RuntimeError("Local LLM returned no choices")

    message = choices[0].get("message", {})
    content = str(message.get("content", "")).strip()
    if not content:
        raise RuntimeError("Local LLM returned empty content")

    return {
        "model": model,
        "content": content,
        "raw_id": body.get("id"),
    }


runtime = Runtime()
app = FastAPI(title="FATHER Chassis / Factory", version=VERSION)


@app.get("/")
def root() -> dict:
    return {"service": "FATHER Chassis / Factory", "version": VERSION, "status": "running"}


@app.get("/health/live")
def live() -> dict:
    return {"live": runtime.health(), "version": VERSION}


@app.get("/health/ready")
def ready() -> dict:
    if runtime.emergency_stop or not runtime.health():
        raise HTTPException(
            status_code=503,
            detail={"ready": False, "emergency_stop": runtime.emergency_stop},
        )
    return {
        "ready": True,
        "blocks": {
            "runtime": True,
            "persistent_state": True,
            "persistent_audit": True,
            "knowledge": True,
        },
    }


@app.post("/ingest")
def ingest(body: IngestBody) -> dict:
    return {"source": body.source, "chunks": runtime.ingest(body.source, body.text)}


@app.post("/run")
def run(body: RunBody) -> dict:
    try:
        return runtime.run(body.input)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/audit/{trace_id}")
def audit(trace_id: str) -> dict:
    return {"trace_id": trace_id, "events": runtime.audit_by_trace(trace_id)}


@app.get("/models")
def models() -> dict:
    result = [{"name": "grounded-rc-fallback", "healthy": True, "default": True}]
    model = os.getenv("FATHER_MODEL_NAME", "").strip()
    if model:
        result.append({"name": model, "healthy": None, "default": False})
    return {"models": result}


@app.get("/models/local/probe")
def local_model_probe() -> dict:
    base_url = os.getenv("FATHER_MODEL_BASE_URL", "").strip()
    model = os.getenv("FATHER_MODEL_NAME", "").strip()
    if not base_url:
        return {
            "configured": False,
            "reachable": False,
            "selected_present": False,
            "models": [],
        }
    try:
        req = urllib.request.Request(
            base_url.rstrip("/") + "/models",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        advertised = [
            str(item.get("id"))
            for item in payload.get("data", [])
            if isinstance(item, dict) and item.get("id")
        ]
        return {
            "configured": True,
            "base_url": base_url,
            "model": model,
            "reachable": True,
            "selected_present": model in advertised if model else bool(advertised),
            "models": advertised,
            "error": None,
        }
    except Exception as exc:
        return {
            "configured": True,
            "base_url": base_url,
            "model": model,
            "reachable": False,
            "selected_present": False,
            "models": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


@app.post("/qualification/knowledge")
def qualification_knowledge() -> dict:
    source_text = (
        "FATHER Chassis is a reusable production platform for agent systems. "
        "It provides state, workflow, model routing, RAG, evidence, audit and safety controls."
    )
    chunks = runtime.ingest("qualification-rc1", source_text)
    result = runtime.run("What is FATHER Chassis and which shared capabilities does it provide?")

    evidence_text = "\n\n".join(
        str(item.get("text", "")) for item in result["evidence"][:5]
    )
    prompt = (
        "Question: What is FATHER Chassis and which shared capabilities does it provide?\n\n"
        "Evidence:\n" + evidence_text
    )

    try:
        llm = call_local_llm(prompt)
        llm_ok = bool(llm["content"].strip())
        runtime.audit(
            result["trace_id"],
            "model.inference.completed",
            {
                "model": llm["model"],
                "output": llm["content"],
                "raw_id": llm["raw_id"],
            },
        )
        error = None
    except Exception as exc:
        llm = {"model": os.getenv("FATHER_MODEL_NAME", "").strip(), "content": ""}
        llm_ok = False
        error = f"{type(exc).__name__}: {exc}"
        runtime.audit(
            result["trace_id"],
            "model.inference.failed",
            {"error": error, "model": llm["model"]},
        )

    audit_events = runtime.audit_by_trace(result["trace_id"])
    passed = (
        chunks > 0
        and len(result["evidence"]) > 0
        and llm_ok
        and any(e["type"] == "model.inference.completed" for e in audit_events)
    )

    return {
        "ingest_chunks": chunks,
        "trace_id": result["trace_id"],
        "evidence_count": len(result["evidence"]),
        "output_nonempty": llm_ok,
        "model": llm["model"],
        "model_output": llm["content"],
        "real_inference": llm_ok,
        "audit_event_count": len(audit_events),
        "error": error,
        "passed": passed,
    }


@app.post("/products/osint/workflow")
def osint_workflow(body: OSINTWorkflowBody) -> dict:
    normalized = []
    total_chunks = 0
    for raw in body.sources:
        source_id = raw.source_id or str(uuid4())[:16]
        text = " ".join(raw.content.split())
        payload = (
            f"[SOURCE_ID={source_id}] [TYPE={raw.source_type.lower()}] "
            f"[TITLE={raw.title.strip()}] [URI={raw.uri or ''}] {text}"
        )
        total_chunks += runtime.ingest(source_id, payload)
        normalized.append(
            {
                "source_id": source_id,
                "source_type": raw.source_type.lower(),
                "title": raw.title.strip(),
                "content": text,
                "uri": raw.uri,
                "collected_at": utcnow(),
            }
        )

    result = runtime.run(body.query)
    source_ids = []
    for ev in result["evidence"]:
        text = str(ev.get("text", ""))
        marker = "[SOURCE_ID="
        if marker in text:
            sid = text.split(marker, 1)[1].split("]", 1)[0]
            if sid and sid not in source_ids:
                source_ids.append(sid)

    report = {
        "product_id": PRODUCT_ID,
        "query": body.query,
        "trace_id": result["trace_id"],
        "answer": result["output"],
        "evidence_count": len(result["evidence"]),
        "source_ids": source_ids,
        "sources": normalized,
        "claims": [{
            "claim": result["output"],
            "status": "SUPPORTED" if result["evidence"] else "UNVERIFIED",
            "evidence_count": len(result["evidence"]),
            "source_ids": source_ids,
        }],
        "status": "PASS" if result["evidence"] and result["output"].strip() else "FAIL",
    }
    response = {
        "product_id": PRODUCT_ID,
        "ingestion": {
            "accepted_sources": len(normalized),
            "chunks": total_chunks,
            "sources": normalized,
        },
        "report": report,
        "audit_event_count": len(runtime.audit_by_trace(result["trace_id"])),
        "passed": (
            len(normalized) > 0
            and total_chunks > 0
            and report["status"] == "PASS"
            and len(source_ids) > 0
        ),
    }
    if not response["passed"]:
        raise HTTPException(status_code=500, detail=response)
    return response


@app.post("/control/stop")
def stop() -> dict:
    runtime.emergency_stop = True
    return {"emergency_stop": True}


@app.post("/control/resume")
def resume() -> dict:
    runtime.emergency_stop = False
    return {"emergency_stop": False}


@app.post("/approvals/{approval_id}")
def approve(approval_id: str) -> dict:
    return {"approval_id": approval_id, "status": "approved", "mode": "rc-recovery-runtime"}
