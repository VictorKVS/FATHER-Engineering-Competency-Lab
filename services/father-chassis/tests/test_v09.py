from pathlib import Path
import json

from fastapi.testclient import TestClient
from father.api import create_app
from father.bootstrap import build_runtime
from father.products.osint_knowledge import OSINTKnowledgeProduct, SourceRecord

ROOT = Path(__file__).resolve().parents[1]

def test_osint_product_full_workflow(tmp_path):
    rt=build_runtime(config_path=ROOT/"config"/"chassis.json", data_dir=tmp_path)
    p=OSINTKnowledgeProduct(rt)
    result=p.full_workflow([
        SourceRecord("s1","document","Architecture","FATHER Chassis provides reusable RAG, evidence, audit and model routing.","local://a"),
        SourceRecord("s2","document","Factory","FATHER Factory assembles products from shared blocks.","local://b"),
    ], "What does FATHER provide?")
    assert result["passed"]
    assert result["ingestion"]["accepted_sources"] == 2
    assert result["report"]["evidence_count"] >= 1
    assert result["report"]["source_ids"]
    assert result["audit_event_count"] >= 2

def test_osint_api_workflow(tmp_path):
    rt=build_runtime(config_path=ROOT/"config"/"chassis.json", data_dir=tmp_path)
    client=TestClient(create_app(rt))
    res=client.post("/products/osint/workflow", json={
        "query":"What is FATHER?",
        "sources":[
            {"source_id":"api1","source_type":"document","title":"Note","content":"FATHER is a reusable chassis for agent systems.","uri":"local://note"}
        ]
    })
    assert res.status_code == 200
    body=res.json()
    assert body["passed"]
    assert body["report"]["product_id"]=="FTH-PRODUCT-OSINT-KNOWLEDGE-001"

def test_osint_bom_reuse_ratio():
    bom=json.loads((ROOT/"products"/"osint_knowledge_bom_0_9.json").read_text(encoding="utf-8"))
    assert bom["reuse_ratio"] >= 0.9
    assert "rag" in bom["shared_blocks"]
    assert "osint_source_normalizer" in bom["product_specific_blocks"]

def test_osint_qualification_script_exists():
    p=ROOT/"scripts"/"osint_product_test.ps1"
    assert p.exists()
    assert "OSINT PRODUCT QUALIFICATION: PASS" in p.read_text(encoding="utf-8")
