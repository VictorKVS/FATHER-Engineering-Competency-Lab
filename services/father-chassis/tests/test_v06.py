from pathlib import Path

from fastapi.testclient import TestClient

from father.api import create_app
from father.bootstrap import build_runtime
from father.core.audit import SQLiteAuditStore


def runtime(tmp_path: Path):
    return build_runtime(
        config_path="config/chassis.json",
        data_dir=tmp_path,
        audit=SQLiteAuditStore(tmp_path / "audit.db"),
    )


def test_persistent_audit_survives_reopen(tmp_path):
    rt = runtime(tmp_path)
    result = rt.run(__import__("father.core.contracts", fromlist=["ExecutionRequest"]).ExecutionRequest("father chassis"))
    trace_id = result.trace.trace_id
    reopened = SQLiteAuditStore(tmp_path / "audit.db")
    events = reopened.by_trace(trace_id)
    assert events[0].type == "request.received"
    assert events[-1].type == "request.completed"


def test_api_ingest_run_and_audit(tmp_path):
    rt = runtime(tmp_path)
    client = TestClient(create_app(rt))
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 200
    ing = client.post("/ingest", json={"source": "manual", "text": "FATHER is a reusable chassis for agent systems."})
    assert ing.status_code == 200 and ing.json()["chunks"] >= 1
    res = client.post("/run", json={"input": "What is FATHER?"})
    assert res.status_code == 200
    body = res.json()
    assert body["trace_id"]
    assert body["evidence"]
    audit = client.get(f"/audit/{body['trace_id']}")
    assert audit.status_code == 200
    assert any(e["type"] == "request.completed" for e in audit.json()["events"])


def test_emergency_stop_visible_through_api(tmp_path):
    client = TestClient(create_app(runtime(tmp_path)))
    assert client.post("/control/stop").json()["emergency_stop"] is True
    assert client.get("/health/ready").status_code == 503
    assert client.post("/run", json={"input": "test"}).status_code == 503
    assert client.post("/control/resume").json()["emergency_stop"] is False
    assert client.get("/health/ready").status_code == 200


def test_model_inventory_endpoint(tmp_path):
    client = TestClient(create_app(runtime(tmp_path)))
    res = client.get("/models")
    assert res.status_code == 200
    assert len(res.json()["models"]) >= 2
