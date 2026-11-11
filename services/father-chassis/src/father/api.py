from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os

from father.core.approval import ApprovalRequired
from father.core.contracts import ExecutionRequest
from father.core.health import health_report
from father.production import build_runtime_from_env
from father.local_llm import probe_openai_compatible
from father.qualification import qualify_knowledge_flow


class RunBody(BaseModel):
    input: str = Field(min_length=1)
    model: str | None = None
    role: str = "agent"
    approval_id: str | None = None


class IngestBody(BaseModel):
    source: str = Field(min_length=1)
    text: str = Field(min_length=1)


def create_app(runtime=None) -> FastAPI:
    runtime = runtime or build_runtime_from_env()
    app = FastAPI(title="FATHER Chassis", version="0.8.0")
    app.state.runtime = runtime

    @app.get("/")
    def root() -> dict:
        return {"service": "FATHER Chassis", "version": "0.8.0", "status": "running"}

    @app.get("/health/live")
    def live() -> dict:
        report = health_report(runtime.registry, runtime.emergency_stop)
        return {"live": report.live, "version": "0.8.0"}

    @app.get("/health/ready")
    def ready() -> dict:
        report = health_report(runtime.registry, runtime.emergency_stop)
        if not report.ready:
            raise HTTPException(status_code=503, detail={"ready": False, "blocks": report.blocks, "emergency_stop": report.emergency_stop})
        return {"ready": True, "blocks": report.blocks}

    @app.get("/models")
    def models() -> dict:
        result = []
        for name, model in runtime.models._models.items():
            checker = getattr(model, "health", None)
            healthy = bool(checker()) if callable(checker) else True
            result.append({"name": name, "healthy": healthy, "default": name == runtime.models.default})
        return {"models": result}

    @app.get("/models/local/probe")
    def local_model_probe() -> dict:
        base_url = os.getenv("FATHER_MODEL_BASE_URL", "").strip()
        model = os.getenv("FATHER_MODEL_NAME", "").strip()
        if not base_url:
            return {"configured": False, "reachable": False, "selected_present": False, "models": []}
        p = probe_openai_compatible(base_url, model)
        return {
            "configured": True,
            "base_url": p.base_url,
            "model": p.model,
            "reachable": p.reachable,
            "selected_present": p.selected_present,
            "models": list(p.advertised_models),
            "error": p.error,
        }

    @app.post("/ingest")
    def ingest(body: IngestBody) -> dict:
        ingester = getattr(runtime.rag, "ingest", None)
        if not callable(ingester):
            raise HTTPException(status_code=501, detail="configured RAG adapter does not support ingestion")
        chunks = ingester(body.source, body.text)
        return {"source": body.source, "chunks": chunks}

    @app.post("/run")
    def run(body: RunBody) -> dict:
        metadata = {"role": body.role}
        if body.model:
            metadata["model"] = body.model
        if body.approval_id:
            metadata["approval_id"] = body.approval_id
        try:
            result = runtime.run(ExecutionRequest(input=body.input, metadata=metadata))
        except ApprovalRequired as exc:
            raise HTTPException(status_code=409, detail={"error": "approval_required", "approval_id": exc.approval_id, "action": exc.action}) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {
            "output": result.output,
            "trace_id": result.trace.trace_id,
            "workflow_id": result.trace.workflow_id,
            "evidence": result.evidence,
            "events": [{"type": e.type, "ts": e.ts, "payload": e.payload} for e in result.events],
        }

    @app.post("/qualification/knowledge")
    def qualification_knowledge() -> dict:
        r = qualify_knowledge_flow(
            runtime,
            source="qualification-0.8",
            text="FATHER Chassis is a reusable production platform for agent systems. It provides shared runtime, state, model routing, RAG, evidence, audit and safety controls.",
            question="What is FATHER Chassis and which shared capabilities does it provide?",
        )
        return r.to_dict()

    @app.get("/audit/{trace_id}")
    def audit(trace_id: str) -> dict:
        events = runtime.audit.by_trace(trace_id)
        return {"trace_id": trace_id, "events": [{"type": e.type, "ts": e.ts, "payload": e.payload} for e in events]}

    @app.post("/approvals/{approval_id}")
    def approve(approval_id: str) -> dict:
        try:
            rec = runtime.approval_gate.approve(approval_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="unknown approval_id") from exc
        return {"approval_id": rec.approval_id, "action": rec.action, "status": rec.status}

    @app.post("/control/stop")
    def stop() -> dict:
        runtime.emergency_stop.engage()
        return {"emergency_stop": True}

    @app.post("/control/resume")
    def resume() -> dict:
        runtime.emergency_stop.release()
        return {"emergency_stop": False}

    return app


app = create_app()
