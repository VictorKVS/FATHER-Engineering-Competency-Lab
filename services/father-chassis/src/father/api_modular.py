from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from father.core.access_control import ClearanceLevel, ResourceContext, SubjectContext
from father.core.approval import ApprovalRequired
from father.core.contracts import ExecutionRequest
from father.core.health import health_report
from father.local_llm import probe_openai_compatible
from father.products.osint_knowledge import OSINTKnowledgeProduct, SourceRecord
from father.domain.kii_engine import KIIDecisionEngine
from father.core.decision_trace import NormReference
from father.production import build_runtime_from_env
from father.qualification import qualify_knowledge_flow
from father.core.agent_manifest import AgentManifest
from father.factory.agent_factory import AgentFactory
from father.factory.reference_catalog import build_reference_capabilities, build_reference_providers
from father.factory.requirement_planner import CustomerRequirement, RequirementPlanner
from father.factory.solution_factory import CustomerSolutionFactory
from father.factory.executor import FactoryExecutor

VERSION = "1.0.0rc1-modular"


class OSINTSourceBody(BaseModel):
    source_id: str = ""
    source_type: str = "text"
    title: str
    content: str
    uri: str | None = None


class OSINTWorkflowBody(BaseModel):
    query: str = Field(min_length=1)
    sources: list[OSINTSourceBody]


class RunBody(BaseModel):
    input: str = Field(min_length=1)
    model: str | None = None
    role: str = "agent"
    approval_id: str | None = None
    subject_id: str | None = None
    roles: list[str] = []
    clearance: str | None = None
    projects: list[str] = []
    compartments: list[str] = []
    resource_id: str | None = None
    resource_classification: str | None = None
    resource_project: str | None = None
    resource_compartments: list[str] = []
    permission: str = "execute:analysis"


class IngestBody(BaseModel):
    source: str = Field(min_length=1)
    text: str = Field(min_length=1)


class CustomerRequirementBody(BaseModel):
    requirement_id: str
    title: str
    needs: list[str]
    constraints: list[str] = []
    required_permissions: list[str] = []
    approval_required_for: list[str] = []
    metadata: dict[str, str] = {}


class FactoryExecuteBody(BaseModel):
    requirement: CustomerRequirementBody
    input: str = Field(min_length=1)
    approval_id: str | None = None
    subject_id: str | None = None
    roles: list[str] = []
    clearance: str | None = None
    projects: list[str] = []
    compartments: list[str] = []
    resource_id: str | None = None
    resource_classification: str | None = None
    resource_project: str | None = None
    resource_compartments: list[str] = []
    permission: str = "execute:analysis"


class AgentManifestBody(BaseModel):
    agent_id: str
    version: str = "0.1.0"
    capabilities: list[str]
    required_permissions: list[str] = []
    required_providers: list[str] = []
    approval_required_for: list[str] = []
    max_steps: int = 12
    timeout_seconds: int = 120
    max_cost_usd: float | None = None


class KIIDecisionBody(BaseModel):
    subject_id: str
    roles: list[str]
    clearance: str
    compartments: list[str] = []
    object_id: str
    resource_classification: str
    resource_compartments: list[str] = []
    object_facts: str
    norm_source_id: str
    norm_title: str
    norm_requirement_id: str
    norm_locator: str
    norm_version: str
    proposed_decision: str


def create_app(runtime=None) -> FastAPI:
    runtime = runtime or build_runtime_from_env()
    app = FastAPI(title="FATHER Chassis Modular", version=VERSION)
    app.state.runtime = runtime

    @app.get("/")
    def root() -> dict:
        return {"service": "FATHER Chassis Modular", "version": VERSION, "status": "running"}

    @app.get("/health/live")
    def live() -> dict:
        report = health_report(runtime.registry, runtime.emergency_stop)
        return {"live": report.live, "version": VERSION}

    @app.get("/health/ready")
    def ready() -> dict:
        report = health_report(runtime.registry, runtime.emergency_stop)
        if not report.ready:
            raise HTTPException(
                status_code=503,
                detail={"ready": False, "blocks": report.blocks, "emergency_stop": report.emergency_stop},
            )
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
        return {"source": body.source, "chunks": ingester(body.source, body.text)}

    @app.post("/run")
    def run(body: RunBody) -> dict:
        metadata = {"role": body.role}
        if body.model:
            metadata["model"] = body.model
        if body.approval_id:
            metadata["approval_id"] = body.approval_id

        if body.subject_id or body.resource_id:
            if not body.subject_id or not body.resource_id or not body.clearance or not body.resource_classification:
                raise HTTPException(
                    status_code=400,
                    detail="subject_id, resource_id, clearance and resource_classification are required together",
                )
            try:
                subject = SubjectContext(
                    subject_id=body.subject_id,
                    roles=frozenset(body.roles),
                    clearance=ClearanceLevel[body.clearance.upper()],
                    projects=frozenset(body.projects),
                    compartments=frozenset(body.compartments),
                )
                resource = ResourceContext(
                    resource_id=body.resource_id,
                    classification=ClearanceLevel[body.resource_classification.upper()],
                    project_id=body.resource_project,
                    compartments=frozenset(body.resource_compartments),
                )
            except KeyError as exc:
                raise HTTPException(status_code=400, detail=f"unknown clearance level: {exc}") from exc
            metadata["subject_context"] = subject
            metadata["resource_context"] = resource
            metadata["permission"] = body.permission
        try:
            result = runtime.run(ExecutionRequest(input=body.input, metadata=metadata))
        except ApprovalRequired as exc:
            raise HTTPException(
                status_code=409,
                detail={"error": "approval_required", "approval_id": exc.approval_id, "action": exc.action},
            ) from exc
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

    @app.get("/audit/{trace_id}")
    def audit(trace_id: str) -> dict:
        events = runtime.audit.by_trace(trace_id)
        return {"trace_id": trace_id, "events": [{"type": e.type, "ts": e.ts, "payload": e.payload} for e in events]}

    @app.post("/products/osint/workflow")
    def osint_workflow(body: OSINTWorkflowBody) -> dict:
        product = OSINTKnowledgeProduct(runtime)
        sources = [
            SourceRecord(
                source_id=s.source_id,
                source_type=s.source_type,
                title=s.title,
                content=s.content,
                uri=s.uri,
            )
            for s in body.sources
        ]
        result = product.full_workflow(sources, body.query)
        if not result["passed"]:
            raise HTTPException(status_code=500, detail=result)
        return result

    @app.post("/factory/solutions/execute")
    def execute_solution(body: FactoryExecuteBody) -> dict:
        req_body = body.requirement
        requirement = CustomerRequirement(
            requirement_id=req_body.requirement_id,
            title=req_body.title,
            needs=frozenset(req_body.needs),
            constraints=frozenset(req_body.constraints),
            required_permissions=frozenset(req_body.required_permissions),
            approval_required_for=frozenset(req_body.approval_required_for),
            metadata=dict(req_body.metadata),
        )

        subject = None
        resource = None
        if body.subject_id or body.resource_id:
            if not body.subject_id or not body.resource_id or not body.clearance or not body.resource_classification:
                raise HTTPException(
                    status_code=400,
                    detail="subject_id, resource_id, clearance and resource_classification are required together",
                )
            try:
                subject = SubjectContext(
                    subject_id=body.subject_id,
                    roles=frozenset(body.roles),
                    clearance=ClearanceLevel[body.clearance.upper()],
                    projects=frozenset(body.projects),
                    compartments=frozenset(body.compartments),
                )
                resource = ResourceContext(
                    resource_id=body.resource_id,
                    classification=ClearanceLevel[body.resource_classification.upper()],
                    project_id=body.resource_project,
                    compartments=frozenset(body.resource_compartments),
                )
            except KeyError as exc:
                raise HTTPException(status_code=400, detail=f"unknown clearance level: {exc}") from exc

        executor = FactoryExecutor(
            runtime=runtime,
            planner=RequirementPlanner(),
            agent_factory=AgentFactory(
                build_reference_capabilities(),
                build_reference_providers(runtime),
            ),
        )
        try:
            result = executor.execute(
                requirement=requirement,
                user_input=body.input,
                subject=subject,
                resource=resource,
                permission=body.permission,
                approval_id=body.approval_id,
            )
        except ApprovalRequired as exc:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "approval_required",
                    "approval_id": exc.approval_id,
                    "action": exc.action,
                },
            ) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return result.to_dict()

    @app.post("/factory/solutions/plan")
    def plan_solution(body: CustomerRequirementBody) -> dict:
        requirement = CustomerRequirement(
            requirement_id=body.requirement_id,
            title=body.title,
            needs=frozenset(body.needs),
            constraints=frozenset(body.constraints),
            required_permissions=frozenset(body.required_permissions),
            approval_required_for=frozenset(body.approval_required_for),
            metadata=dict(body.metadata),
        )
        solution_factory = CustomerSolutionFactory(
            RequirementPlanner(),
            AgentFactory(
                build_reference_capabilities(),
                build_reference_providers(runtime),
            ),
        )
        return solution_factory.plan(requirement)

    @app.post("/factory/agents/plan")
    def plan_agent(body: AgentManifestBody) -> dict:
        manifest = AgentManifest(
            agent_id=body.agent_id,
            version=body.version,
            capabilities=frozenset(body.capabilities),
            required_permissions=frozenset(body.required_permissions),
            required_providers=frozenset(body.required_providers),
            approval_required_for=frozenset(body.approval_required_for),
            max_steps=body.max_steps,
            timeout_seconds=body.timeout_seconds,
            max_cost_usd=body.max_cost_usd,
        )
        factory = AgentFactory(
            build_reference_capabilities(),
            build_reference_providers(runtime),
        )
        return factory.plan(manifest).to_dict()

    @app.post("/factory/agents/build")
    def build_agent(body: AgentManifestBody) -> dict:
        manifest = AgentManifest(
            agent_id=body.agent_id,
            version=body.version,
            capabilities=frozenset(body.capabilities),
            required_permissions=frozenset(body.required_permissions),
            required_providers=frozenset(body.required_providers),
            approval_required_for=frozenset(body.approval_required_for),
            max_steps=body.max_steps,
            timeout_seconds=body.timeout_seconds,
            max_cost_usd=body.max_cost_usd,
        )
        factory = AgentFactory(
            build_reference_capabilities(),
            build_reference_providers(runtime),
        )
        try:
            profile = factory.build(manifest)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"agent_id": profile.agent_id, "build_plan": profile.build_plan.to_dict()}

    @app.post("/compliance/kii/decision")
    def kii_decision(body: KIIDecisionBody) -> dict:
        try:
            subject = SubjectContext(
                subject_id=body.subject_id,
                roles=frozenset(body.roles),
                clearance=ClearanceLevel[body.clearance.upper()],
                compartments=frozenset(body.compartments),
            )
            resource = ResourceContext(
                resource_id=body.object_id,
                classification=ClearanceLevel[body.resource_classification.upper()],
                compartments=frozenset(body.resource_compartments),
            )
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"unknown clearance level: {exc}") from exc

        norm = NormReference(
            source_id=body.norm_source_id,
            title=body.norm_title,
            requirement_id=body.norm_requirement_id,
            locator=body.norm_locator,
            version=body.norm_version,
        )
        try:
            return KIIDecisionEngine(runtime.access_control).assess(
                subject=subject,
                resource=resource,
                object_id=body.object_id,
                object_facts=body.object_facts,
                norm=norm,
                proposed_decision=body.proposed_decision,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @app.post("/qualification/knowledge")
    def qualification_knowledge() -> dict:
        return qualify_knowledge_flow(
            runtime,
            source="qualification-modular",
            text=(
                "FATHER Chassis is a reusable production platform for agent systems. "
                "It provides shared runtime, state, model routing, RAG, evidence, audit and safety controls."
            ),
            question="What is FATHER Chassis and which shared capabilities does it provide?",
        ).to_dict()

    @app.post("/control/stop")
    def stop() -> dict:
        runtime.emergency_stop.engage()
        return {"emergency_stop": True}

    @app.post("/control/resume")
    def resume() -> dict:
        runtime.emergency_stop.release()
        return {"emergency_stop": False}

    @app.post("/approvals/{approval_id}")
    def approve(approval_id: str) -> dict:
        try:
            rec = runtime.approval_gate.approve(approval_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="unknown approval_id") from exc
        return {"approval_id": rec.approval_id, "action": rec.action, "status": rec.status}

    return app


app = create_app()
