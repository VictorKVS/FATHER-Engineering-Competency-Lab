param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_m6_qualified_kb_admission_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_M6_QUALIFIED_KB_ADMISSION"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 qualified_kb_admitted=$false
 missing_kb_blocked=$false
 unqualified_kb_blocked=$false
 missing_provenance_blocked=$false
 missing_retrieval_blocked=$false
 kb_trace_preserved=$false
 restart_trace_preserved=$false
 strict_mode_fail_closed=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[G7 M6] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[G7 M6] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:G7_M6_ARTIFACT=$artifactPath

@'
import json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path

from father.core.state import SQLiteStateStore
from father.engineering.factory_agents import build_factory_agent_catalog
from father.engineering.factory_orchestrator import FactoryEngineeringWorkflow, StageArtifact
from father.engineering.knowledge_admission import (
    InMemoryKnowledgeReleaseRegistry,
    KnowledgeBaseRelease,
    QualifiedKnowledgeAdmissionGate,
)
from father.engineering.stage_artifacts import CustomerRequestPayload
from father.engineering.delivery_contract import BusinessProcessSpec

artifact_path=Path(os.environ["G7_M6_ARTIFACT"])
catalog=build_factory_agent_catalog()

def rel(status="QUALIFIED", provenance=True, retrieval=True):
    return KnowledgeBaseRelease(
        release_id="REL-KB-BUSINESS-001",
        kb_id="KB-BUSINESS-ANALYSIS",
        version="1.0.0",
        release_hash="a"*64,
        status=status,
        source_set_hashes=("b"*64,),
        provenance_refs=("provenance://business",) if provenance else (),
        retrieval_evidence_refs=("evidence://retrieval-business",) if retrieval else (),
        retrieval_metrics={"recall_at_5":0.91} if retrieval else {},
        created_at="2026-11-13T00:00:00+00:00",
    )

def run(releases):
    gate=QualifiedKnowledgeAdmissionGate(
        catalog=catalog,
        registry=InMemoryKnowledgeReleaseRegistry(tuple(releases)),
    )
    wf=FactoryEngineeringWorkflow(
        knowledge_gate=gate,
        require_knowledge_admission=True,
    )
    wf.add_external_artifact(StageArtifact(
        "REQ","customer_request","HUMAN_APPROVAL",
        CustomerRequestPayload("REQ","t","o"),True
    ))
    return wf.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        StageArtifact(
            "BP","BusinessProcessSpec","FTH-AGENT-BUSINESS-ANALYST",
            BusinessProcessSpec("BP","g",("i",),("o",),("a",),approved=True),True
        )
    )

qualified=run((rel(),))
assert qualified.status=="PASS"
assert qualified.knowledge_release_ids==("REL-KB-BUSINESS-001",)
assert qualified.knowledge_release_hashes==("a"*64,)
assert "provenance://business" in qualified.knowledge_evidence_refs
assert "evidence://retrieval-business" in qualified.knowledge_evidence_refs

assert run(()).status=="BLOCKED"
assert run((rel(status="DRAFT"),)).status=="BLOCKED"
assert run((rel(provenance=False),)).status=="BLOCKED"
assert run((rel(retrieval=False),)).status=="BLOCKED"

strict=False
try:
    FactoryEngineeringWorkflow(require_knowledge_admission=True)
except ValueError:
    strict=True
assert strict

with tempfile.TemporaryDirectory(prefix="father-g7-m6-") as tmp:
    store=SQLiteStateStore(Path(tmp)/"workflow.db")
    gate=QualifiedKnowledgeAdmissionGate(
        catalog=catalog,
        registry=InMemoryKnowledgeReleaseRegistry((rel(),)),
    )
    first=FactoryEngineeringWorkflow(
        store=store,
        workflow_id="WF-G7-M6",
        knowledge_gate=gate,
        require_knowledge_admission=True,
    )
    first.add_external_artifact(StageArtifact(
        "REQ-R","customer_request","HUMAN_APPROVAL",
        CustomerRequestPayload("REQ-R","t","o"),True
    ))
    res=first.submit_stage_artifact(
        "BUSINESS_ANALYSIS",
        StageArtifact(
            "BP-R","BusinessProcessSpec","FTH-AGENT-BUSINESS-ANALYST",
            BusinessProcessSpec("BP-R","g",("i",),("o",),("a",),approved=True),True
        )
    )
    assert res.status=="PASS"
    second=FactoryEngineeringWorkflow(
        store=store,
        workflow_id="WF-G7-M6",
        knowledge_gate=gate,
        require_knowledge_admission=True,
    )
    hist=second.status()["history"][-1]
    assert hist["knowledge_release_ids"]==("REL-KB-BUSINESS-001",)
    assert hist["knowledge_release_hashes"]==("a"*64,)
    assert "evidence://retrieval-business" in hist["knowledge_evidence_refs"]

payload={
 "qualified_kb_admitted":True,
 "missing_kb_blocked":True,
 "unqualified_kb_blocked":True,
 "missing_provenance_blocked":True,
 "missing_retrieval_blocked":True,
 "kb_trace_preserved":True,
 "restart_trace_preserved":True,
 "strict_mode_fail_closed":True,
 "snapshot_schema_version":4,
 "release_id":"REL-KB-BUSINESS-001",
 "release_hash":"a"*64,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Knowledge admission qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @("qualified_kb_admitted","missing_kb_blocked","unqualified_kb_blocked","missing_provenance_blocked","missing_retrieval_blocked","kb_trace_preserved","restart_trace_preserved","strict_mode_fail_closed")){
    $result[$name]=[bool]$runtime.$name
  }
  $result.passed=$result.toolchain_ready -and $result.regression -and $result.qualified_kb_admitted -and $result.missing_kb_blocked -and $result.unqualified_kb_blocked -and $result.missing_provenance_blocked -and $result.missing_retrieval_blocked -and $result.kb_trace_preserved -and $result.restart_trace_preserved -and $result.strict_mode_fail_closed
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 M6 QUALIFIED KB ADMISSION: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 M6 QUALIFIED KB ADMISSION: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
