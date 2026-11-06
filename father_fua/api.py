from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from father_fua.full_assembly import FullFUAAssemblyRuntime


APP_VERSION = "0.1.0"
DEV_TOKEN = os.getenv("FUA_DEV_TOKEN")
security = HTTPBearer(auto_error=False)


def _sha256(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    if DEV_TOKEN is None or credentials is None or credentials.scheme.lower() != "bearer" or credentials.credentials != DEV_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid bearer token")
    return "local-dev-operator"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AgentDefinitionRequest(StrictModel):
    agent_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    mission_profile: str = Field(min_length=1)
    environment: str = Field(min_length=1)
    trust_level: Literal["UNTRUSTED", "RESTRICTED", "STANDARD", "PRIVILEGED"]


class AgentIdentity(AgentDefinitionRequest):
    manifest_sha256: str


class InstanceRequest(StrictModel):
    environment: str = Field(min_length=1)


class AgentInstance(StrictModel):
    agent_id: str
    instance_id: str
    version: str
    created_at: float


class RoleProfile(StrictModel):
    primary_role: str
    allowed_duties: list[str]
    forbidden_duties: list[str]
    jurisdiction: list[str]
    version: str


class MissionRequest(StrictModel):
    mission: str = Field(min_length=1, max_length=10000)
    success_criteria: list[str] = Field(min_length=1)
    failure_criteria: list[str] = Field(min_length=1)
    constraints: list[str]
    priority: int = Field(default=50, ge=0, le=100)
    ttl_seconds: int = Field(default=600, ge=1)


class MissionAccepted(StrictModel):
    mission_id: str
    goal_version: str
    plan_id: str
    status: Literal["ACCEPTED", "PENDING_APPROVAL"]


class MemoryQuery(StrictModel):
    query: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=100)


class MemoryWriteRequest(StrictModel):
    type: Literal["WORKING", "EPISODIC", "SEMANTIC", "PROCEDURAL", "USER_PROJECT"]
    scope: str = Field(min_length=1)
    content: str = Field(min_length=1)
    provenance: str = Field(min_length=1)
    confidence: float = Field(default=1.0, ge=0, le=1)


class AssemblyMissionRequest(StrictModel):
    mission: str = Field(min_length=1, max_length=10000)


class PromptAssemblyRequest(StrictModel):
    prompt_pack: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    model_profile: str = Field(min_length=1)
    context_refs: list[str] = []


@dataclass
class Store:
    agents: dict[str, AgentIdentity] = field(default_factory=dict)
    instances: dict[str, list[AgentInstance]] = field(default_factory=dict)
    roles: dict[str, RoleProfile] = field(default_factory=dict)
    missions: dict[str, dict] = field(default_factory=dict)
    plans: dict[str, dict] = field(default_factory=dict)
    states: dict[str, dict] = field(default_factory=dict)
    memory: dict[str, list[dict]] = field(default_factory=dict)
    audit: list[dict] = field(default_factory=list)

    def event(self, kind: str, agent_id: str, detail: dict) -> None:
        self.audit.append({
            "ts": time.time(),
            "kind": kind,
            "agent_id": agent_id,
            "detail": detail,
        })


store = Store()
app = FastAPI(title="FUA-001 Control Plane API", version=APP_VERSION)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": APP_VERSION}


@app.post("/v1/agents", response_model=AgentIdentity, status_code=201)
def create_agent(req: AgentDefinitionRequest, _: str = Depends(require_auth)) -> AgentIdentity:
    if req.agent_id in store.agents:
        raise HTTPException(status_code=409, detail="agent already exists")
    payload = req.model_dump()
    identity = AgentIdentity(**payload, manifest_sha256=_sha256(payload))
    store.agents[req.agent_id] = identity
    store.roles[req.agent_id] = RoleProfile(
        primary_role="UNASSIGNED",
        allowed_duties=[],
        forbidden_duties=["ALL_PRIVILEGED_ACTIONS"],
        jurisdiction=[],
        version="0.1",
    )
    store.states[req.agent_id] = {
        "revision": 0,
        "session_id": f"bootstrap-{uuid.uuid4()}",
        "state": "REGISTERED",
    }
    store.event("agent.created", req.agent_id, {"manifest_sha256": identity.manifest_sha256})
    return identity


def get_agent_or_404(agent_id: str) -> AgentIdentity:
    agent = store.agents.get(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="agent not found")
    return agent


@app.get("/v1/agents/{agent_id}", response_model=AgentIdentity)
def get_agent(agent_id: str = Path(min_length=1), _: str = Depends(require_auth)) -> AgentIdentity:
    return get_agent_or_404(agent_id)


@app.post("/v1/agents/{agent_id}/instances", response_model=AgentInstance, status_code=201)
def create_instance(agent_id: str, req: InstanceRequest, _: str = Depends(require_auth)) -> AgentInstance:
    agent = get_agent_or_404(agent_id)
    instance = AgentInstance(
        agent_id=agent_id,
        instance_id=str(uuid.uuid4()),
        version=agent.version,
        created_at=time.time(),
    )
    store.instances.setdefault(agent_id, []).append(instance)
    store.event("instance.created", agent_id, {"instance_id": instance.instance_id, "environment": req.environment})
    return instance


@app.get("/v1/agents/{agent_id}/role", response_model=RoleProfile)
def get_role(agent_id: str, _: str = Depends(require_auth)) -> RoleProfile:
    get_agent_or_404(agent_id)
    return store.roles[agent_id]


@app.post("/v1/agents/{agent_id}/missions", response_model=MissionAccepted, status_code=202)
def submit_mission(
    agent_id: str,
    req: MissionRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=16, max_length=128),
    _: str = Depends(require_auth),
) -> MissionAccepted:
    agent = get_agent_or_404(agent_id)
    role = store.roles[agent_id]
    if "ALL_PRIVILEGED_ACTIONS" in role.forbidden_duties and agent.trust_level == "PRIVILEGED":
        raise HTTPException(status_code=403, detail="role policy blocks privileged mission")
    existing = store.missions.get(idempotency_key)
    if existing:
        return MissionAccepted(**existing["accepted"])

    mission_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())
    accepted = MissionAccepted(
        mission_id=mission_id,
        goal_version="1",
        plan_id=plan_id,
        status="ACCEPTED",
    )
    store.missions[idempotency_key] = {"request": req.model_dump(), "accepted": accepted.model_dump()}
    store.plans[plan_id] = {
        "plan_id": plan_id,
        "version": "1",
        "goal_id": mission_id,
        "tasks": [{"task_id": f"{plan_id}:01", "goal_link": mission_id, "status": "PLANNED"}],
        "status": "PLANNED",
    }
    state = store.states[agent_id]
    state["revision"] += 1
    state["state"] = "MISSION_ACCEPTED"
    store.event("mission.accepted", agent_id, {"mission_id": mission_id, "plan_id": plan_id})
    return accepted


@app.get("/v1/agents/{agent_id}/plans/{plan_id}")
def get_plan(agent_id: str, plan_id: str, _: str = Depends(require_auth)) -> dict:
    get_agent_or_404(agent_id)
    plan = store.plans.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="plan not found")
    return plan


@app.get("/v1/agents/{agent_id}/state")
def get_state(agent_id: str, _: str = Depends(require_auth)) -> dict:
    get_agent_or_404(agent_id)
    state = store.states[agent_id].copy()
    state["integrity_sha256"] = _sha256(state)
    return state


@app.post("/v1/agents/{agent_id}/checkpoints", status_code=201)
def create_checkpoint(agent_id: str, _: str = Depends(require_auth)) -> dict:
    get_agent_or_404(agent_id)
    state = store.states[agent_id].copy()
    checkpoint = {
        "checkpoint_id": str(uuid.uuid4()),
        "revision": state["revision"],
        "integrity_sha256": _sha256(state),
    }
    store.event("state.checkpoint", agent_id, checkpoint)
    return checkpoint


@app.post("/v1/agents/{agent_id}/memory/query")
def query_memory(agent_id: str, req: MemoryQuery, _: str = Depends(require_auth)) -> dict:
    get_agent_or_404(agent_id)
    items = [
        item for item in store.memory.get(agent_id, [])
        if item["scope"] == req.scope and req.query.lower() in item["content"].lower()
    ][: req.limit]
    return {"items": items}


@app.post("/v1/agents/{agent_id}/memory", status_code=202)
def request_memory_write(agent_id: str, req: MemoryWriteRequest, _: str = Depends(require_auth)) -> dict:
    get_agent_or_404(agent_id)
    if req.type == "PROCEDURAL":
        decision = "REQUIRE_APPROVAL"
        reason = "procedural memory requires stronger approval"
    elif req.confidence < 0.5:
        decision = "QUARANTINE"
        reason = "confidence below trusted-memory threshold"
    else:
        decision = "ALLOW"
        reason = "prototype local policy accepted write"
        store.memory.setdefault(agent_id, []).append({
            "memory_id": str(uuid.uuid4()),
            **req.model_dump(),
        })
    evidence_id = f"EVID-{uuid.uuid4()}"
    store.event("memory.write_decision", agent_id, {"decision": decision, "evidence_id": evidence_id})
    return {"decision": decision, "reason": reason, "evidence_id": evidence_id}


@app.post("/v1/agents/{agent_id}/prompts/assemble")
def assemble_prompt(agent_id: str, req: PromptAssemblyRequest, _: str = Depends(require_auth)) -> dict:
    get_agent_or_404(agent_id)
    payload = {
        "agent_id": agent_id,
        "prompt_pack": req.prompt_pack,
        "task_id": req.task_id,
        "model_profile": req.model_profile,
        "context_refs": req.context_refs,
    }
    result = {
        "prompt_version": "0.1",
        "prompt_sha256": _sha256(payload),
        "compatibility": "PASS",
        "policy_decision": "ALLOW",
    }
    store.event("prompt.assembled", agent_id, result)
    return result


@app.get("/v1/agents/{agent_id}/readiness")
def readiness(agent_id: str, _: str = Depends(require_auth)) -> dict:
    get_agent_or_404(agent_id)
    return {
        "lifecycle_status": "05.IMPLEMENTED_PROTOTYPE",
        "installation_permit": "DENIED",
        "blocking_gates": [
            "08.SECURITY_TESTED",
            "09.COMPATIBILITY_TESTED",
            "10.INTEGRATION_TESTED",
            "11.RED_TEAM_TESTED",
            "12.POLYGON_TESTED",
            "13.EVIDENCE_AUDITED",
        ],
    }


@app.get("/v1/audit")
def audit(_: str = Depends(require_auth)) -> dict:
    return {"events": store.audit}



@app.post("/v1/assembly/run")
def run_full_assembly(req: AssemblyMissionRequest, _: str = Depends(require_auth)) -> dict:
    runtime = FullFUAAssemblyRuntime()
    runtime.rag.register(
        source_id="API-BOOTSTRAP",
        content="FATHER universal agent architecture runtime evidence",
        provenance="api:bootstrap",
        classification="INTERNAL",
        trust="REVIEWED",
    )
    result = runtime.run(req.mission)
    return {
        "mission_id": result.mission_id,
        "status": result.status,
        "instance_id": result.identity_instance_id,
        "prompt_sha256": result.prompt_sha256,
        "state_sha256": result.state_sha256,
        "evidence_id": result.evidence.evidence_id,
        "evidence_sha256": result.evidence.sha256,
        "readiness": result.readiness,
        "audit_ok": result.audit_ok,
        "answer": result.answer,
    }
