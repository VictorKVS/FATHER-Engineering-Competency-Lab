import os
os.environ["FUA_DEV_TOKEN"]="dev-token"

from fastapi.testclient import TestClient
from father_fua.api import app

client=TestClient(app)
AUTH={"Authorization":"Bearer dev-token"}


def test_assembly_requires_auth():
    r=client.post("/v1/assembly/run",json={"mission":"x"})
    assert r.status_code==401


def test_assembly_rejects_empty_mission():
    r=client.post("/v1/assembly/run",headers=AUTH,json={"mission":""})
    assert r.status_code==422


def test_assembly_rejects_oversized_mission():
    r=client.post("/v1/assembly/run",headers=AUTH,json={"mission":"x"*10001})
    assert r.status_code==422


def test_assembly_rejects_unknown_fields():
    r=client.post("/v1/assembly/run",headers=AUTH,json={"mission":"x","trust_level":"PRIVILEGED"})
    assert r.status_code==422


def test_agent_rejects_invalid_trust_level():
    r=client.post("/v1/agents",headers=AUTH,json={
        "agent_id":"NEG-A","name":"N","version":"1","owner":"FATHER",
        "mission_profile":"TEST","environment":"LOCAL","trust_level":"ROOT"
    })
    assert r.status_code==422


def test_wrong_bearer_token_rejected():
    r=client.get("/v1/audit",headers={"Authorization":"Bearer wrong-token"})
    assert r.status_code==401
