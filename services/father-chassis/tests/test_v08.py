from pathlib import Path
import json

from father.bootstrap import build_runtime
from father.local_llm import ModelProbe
from father.qualification import qualify_knowledge_flow

ROOT = Path(__file__).resolve().parents[1]

def test_knowledge_qualification_flow(tmp_path):
    rt=build_runtime(config_path=ROOT/"config"/"chassis.json", data_dir=tmp_path)
    r=qualify_knowledge_flow(
        rt,
        source="unit",
        text="FATHER provides reusable RAG, evidence and audit capabilities.",
        question="What does FATHER provide?",
    )
    assert r.passed
    assert r.ingest_chunks >= 1
    assert r.evidence_count >= 1
    assert r.audit_event_count >= 2

def test_local_llm_profile_exists():
    p=ROOT/"config"/"local_llm.example.json"
    d=json.loads(p.read_text(encoding="utf-8"))
    assert d["provider"]=="openai-compatible"
    assert d["base_url"].endswith("/v1")

def test_llm_test_script_exists():
    p=ROOT/"scripts"/"llm_test.ps1"
    assert p.exists()
    assert "LOCAL LLM QUALIFICATION: PASS" in p.read_text(encoding="utf-8")

def test_model_probe_value_object():
    p=ModelProbe("http://localhost:1/v1","x",False,(),False,"offline")
    assert p.reachable is False
    assert p.selected_present is False
