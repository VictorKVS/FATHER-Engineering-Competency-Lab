import os

os.environ["FUA_DEV_TOKEN"] = "dev-token"

from fastapi.testclient import TestClient

from father_fua.api import app, store


client = TestClient(app)
AUTH = {"Authorization": "Bearer dev-token"}


def setup_function():
    store.agents.clear()
    store.instances.clear()
    store.roles.clear()
    store.missions.clear()
    store.plans.clear()
    store.states.clear()
    store.memory.clear()
    store.audit.clear()


def create_agent(agent_id="FUA-TEST-001", trust_level="STANDARD"):
    payload = {
        "agent_id": agent_id,
        "name": "Test Agent",
        "version": "0.1",
        "owner": "FATHER",
        "mission_profile": "TEST",
        "environment": "LOCAL",
        "trust_level": trust_level,
    }
    r = client.post("/v1/agents", json=payload, headers=AUTH)
    assert r.status_code == 201
    return r.json()


def test_health_requires_no_auth():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_protected_endpoint_rejects_missing_auth():
    r = client.get("/v1/agents/missing")
    assert r.status_code == 401


def test_identity_contract_and_hash():
    data = create_agent()
    assert len(data["manifest_sha256"]) == 64
    r = client.get("/v1/agents/FUA-TEST-001", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["agent_id"] == "FUA-TEST-001"


def test_duplicate_agent_rejected():
    create_agent()
    r = client.post("/v1/agents", json={
        "agent_id": "FUA-TEST-001", "name": "X", "version": "0.1", "owner": "FATHER",
        "mission_profile": "TEST", "environment": "LOCAL", "trust_level": "STANDARD",
    }, headers=AUTH)
    assert r.status_code == 409


def test_runtime_instance_ids_are_unique():
    create_agent()
    a = client.post("/v1/agents/FUA-TEST-001/instances", json={"environment":"LOCAL"}, headers=AUTH).json()
    b = client.post("/v1/agents/FUA-TEST-001/instances", json={"environment":"LOCAL"}, headers=AUTH).json()
    assert a["instance_id"] != b["instance_id"]


def test_extra_identity_field_rejected():
    payload = {
        "agent_id": "FUA-X", "name": "X", "version": "0.1", "owner": "FATHER",
        "mission_profile": "TEST", "environment": "LOCAL", "trust_level": "STANDARD",
        "model_supplied_trust": "PRIVILEGED",
    }
    r = client.post("/v1/agents", json=payload, headers=AUTH)
    assert r.status_code == 422


def test_mission_requires_idempotency_key():
    create_agent()
    mission = {
        "mission":"test", "success_criteria":["done"], "failure_criteria":["failed"],
        "constraints":[], "ttl_seconds":60
    }
    r = client.post("/v1/agents/FUA-TEST-001/missions", json=mission, headers=AUTH)
    assert r.status_code == 422


def test_mission_is_idempotent():
    create_agent()
    mission = {
        "mission":"test", "success_criteria":["done"], "failure_criteria":["failed"],
        "constraints":[], "ttl_seconds":60
    }
    h = {**AUTH, "Idempotency-Key":"0123456789abcdef"}
    a = client.post("/v1/agents/FUA-TEST-001/missions", json=mission, headers=h)
    b = client.post("/v1/agents/FUA-TEST-001/missions", json=mission, headers=h)
    assert a.status_code == 202
    assert b.status_code == 202
    assert a.json()["mission_id"] == b.json()["mission_id"]


def test_state_integrity_and_checkpoint():
    create_agent()
    s = client.get("/v1/agents/FUA-TEST-001/state", headers=AUTH)
    assert s.status_code == 200
    assert len(s.json()["integrity_sha256"]) == 64
    c = client.post("/v1/agents/FUA-TEST-001/checkpoints", headers=AUTH)
    assert c.status_code == 201
    assert len(c.json()["integrity_sha256"]) == 64


def test_low_confidence_memory_is_quarantined():
    create_agent()
    r = client.post("/v1/agents/FUA-TEST-001/memory", headers=AUTH, json={
        "type":"SEMANTIC", "scope":"TEST", "content":"untrusted claim",
        "provenance":"SRC-X", "confidence":0.2
    })
    assert r.status_code == 202
    assert r.json()["decision"] == "QUARANTINE"


def test_procedural_memory_requires_approval():
    create_agent()
    r = client.post("/v1/agents/FUA-TEST-001/memory", headers=AUTH, json={
        "type":"PROCEDURAL", "scope":"TEST", "content":"new procedure",
        "provenance":"SRC-X", "confidence":0.9
    })
    assert r.status_code == 202
    assert r.json()["decision"] == "REQUIRE_APPROVAL"


def test_prompt_assembly_is_hash_addressed():
    create_agent()
    r = client.post("/v1/agents/FUA-TEST-001/prompts/assemble", headers=AUTH, json={
        "prompt_pack":"PACK-1","task_id":"TASK-1","model_profile":"MODEL-1","context_refs":["SRC-1"]
    })
    assert r.status_code == 200
    assert len(r.json()["prompt_sha256"]) == 64


def test_readiness_stays_denied():
    create_agent()
    r = client.get("/v1/agents/FUA-TEST-001/readiness", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["installation_permit"] == "DENIED"
    assert r.json()["blocking_gates"]



def test_full_assembly_api_endpoint():
    r = client.post(
        "/v1/assembly/run",
        headers=AUTH,
        json={"mission": "FATHER universal agent architecture"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "PASS"
    assert body["audit_ok"] is True
    assert body["readiness"] == "DENIED"
    assert len(body["prompt_sha256"]) == 64
    assert len(body["state_sha256"]) == 64
    assert len(body["evidence_sha256"]) == 64
