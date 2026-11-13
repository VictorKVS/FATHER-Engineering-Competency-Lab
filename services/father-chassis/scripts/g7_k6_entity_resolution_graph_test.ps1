param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$serviceDir = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $serviceDir "artifacts\local"
$artifactPath = Join-Path $artifactDir "g7_k6_entity_resolution_graph_qualification_2026-11-13.json"
New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

$result=[ordered]@{
 qualification="G7_K6_ENTITY_RESOLUTION_GRAPH"
 started_at_utc=(Get-Date).ToUniversalTime().ToString("o")
 toolchain_ready=$false
 regression=$false
 exact_merge_passed=$false
 merge_lineage_preserved=$false
 type_conflict_explicit=$false
 relation_endpoints_resolved=$false
 duplicate_edges_deduplicated=$false
 dangling_relation_rejected=$false
 input_order_independent=$false
 policy_version_changes_identity=$false
 no_inferred_edges=$false
 invalid_policy_rejected=$false
 passed=$false
}

try {
 Push-Location $serviceDir
 try {
  & $Python -m ruff --version *> $null
  if($LASTEXITCODE -ne 0){ throw "QUALIFICATION_ENVIRONMENT_BLOCKED: ruff missing" }
  $result.toolchain_ready=$true

  Write-Host "[G7 K6] Ruff"
  & $Python -m ruff check src tests --select F821,F822,F823
  if($LASTEXITCODE -ne 0){ throw "Ruff failed" }

  Write-Host "[G7 K6] Chassis regression"
  & $Python -m pytest -q
  if($LASTEXITCODE -ne 0){ throw "Regression failed" }
  $result.regression=$true

  $env:PYTHONPATH=(Join-Path $serviceDir "src")
  $env:G7_K6_ARTIFACT=$artifactPath

@'
import json, os
from datetime import datetime, timezone
from pathlib import Path

from father.knowledge_factory.entity_graph import (
    DeterministicEntityGraphBuilder,
    GraphResolutionPolicy,
)
from father.knowledge_factory.entity_relation import (
    EntityRecord,
    ExtractionSet,
    RelationRecord,
)

artifact_path=Path(os.environ["G7_K6_ARTIFACT"])

def entity(eid,name,etype="TERM",evidence=("CHK-1",),hash_char="a"):
    return EntityRecord(eid,etype,name,(),0.9,evidence,hash_char*64)

def relation(rid,subject,obj,evidence=("CHK-1",),hash_char="r"):
    return RelationRecord(rid,"POINTS_TO",subject,obj,0.95,evidence,hash_char*64)

def exset(sid,entities,relations=(),hash_char="a"):
    return ExtractionSet(
        extraction_set_id=sid,
        chunk_set_id="CHSET-"+sid,
        chunk_set_hash=hash_char*64,
        extractor_id="EXTRACTOR",
        extractor_version="1.0",
        policy_id="POL-E",
        policy_version="1.0",
        entities=tuple(entities),
        relations=tuple(relations),
        extraction_set_hash=hash_char*64,
    )

builder=DeterministicEntityGraphBuilder()
policy=GraphResolutionPolicy("POL-K6","1.0")

a1=entity("ENT-A1","Alpha",evidence=("CHK-1",),hash_char="a")
b1=entity("ENT-B1","Beta",evidence=("CHK-1",),hash_char="b")
r1=relation("REL-R1","ENT-A1","ENT-B1",evidence=("CHK-1",),hash_char="c")
first=exset("EX-1",(a1,b1),(r1,),hash_char="d")

a2=entity("ENT-A2"," alpha ",evidence=("CHK-2",),hash_char="e")
b2=entity("ENT-B2","Beta",evidence=("CHK-2",),hash_char="f")
r2=relation("REL-R2","ENT-A2","ENT-B2",evidence=("CHK-2",),hash_char="g")
second=exset("EX-2",(a2,b2),(r2,),hash_char="h")

built=builder.build((first,second),policy)
assert built.status=="BUILT"
alpha_nodes=[n for n in built.graph.nodes if n.canonical_name.casefold()=="alpha"]
assert len(alpha_nodes)==1
assert alpha_nodes[0].source_entity_ids==("ENT-A1","ENT-A2")
assert alpha_nodes[0].evidence_chunk_ids==("CHK-1","CHK-2")
assert len(built.graph.edges)==1
edge=built.graph.edges[0]
node_ids={n.node_id for n in built.graph.nodes}
assert edge.subject_node_id in node_ids and edge.object_node_id in node_ids
assert edge.source_relation_ids==("REL-R1","REL-R2")
assert edge.evidence_chunk_ids==("CHK-1","CHK-2")

conflict_set=exset("EX-C",(entity("ENT-C1","Alpha","ORG",hash_char="i"),),hash_char="j")
with_conflict=builder.build((first,conflict_set),policy)
assert with_conflict.status=="BUILT"
assert any(c.conflict_type=="SAME_NAME_DIFFERENT_TYPE" for c in with_conflict.graph.conflicts)
assert len([n for n in with_conflict.graph.nodes if n.canonical_name.casefold()=="alpha"])==2

dangling=exset(
    "EX-D",
    (entity("ENT-D1","Delta",hash_char="k"),),
    (relation("REL-D1","ENT-D1","ENT-MISSING",hash_char="l"),),
    hash_char="m",
)
bad=builder.build((dangling,),policy)
assert bad.status=="REJECTED"
assert any("dangling relation object" in x for x in bad.diagnostics)

forward=builder.build((first,second),policy)
reverse=builder.build((second,first),policy)
assert forward.graph.graph_hash==reverse.graph.graph_hash
assert forward.graph.graph_id==reverse.graph.graph_id

v2=builder.build((first,second),GraphResolutionPolicy("POL-K6","2.0"))
assert forward.graph.graph_hash!=v2.graph.graph_hash

no_rel=exset("EX-N",(entity("ENT-N1","NodeA",hash_char="n"),entity("ENT-N2","NodeB",hash_char="o")),(),hash_char="p")
no_inferred=builder.build((no_rel,),policy)
assert no_inferred.graph.edges==()

invalid=builder.build((first,),GraphResolutionPolicy("POL-K6","1.0",exact_name_same_type_merge=False))
assert invalid.status=="REJECTED"

payload={
 "exact_merge_passed":True,
 "merge_lineage_preserved":True,
 "type_conflict_explicit":True,
 "relation_endpoints_resolved":True,
 "duplicate_edges_deduplicated":True,
 "dangling_relation_rejected":True,
 "input_order_independent":True,
 "policy_version_changes_identity":True,
 "no_inferred_edges":True,
 "invalid_policy_rejected":True,
 "graph_id":built.graph.graph_id,
 "graph_hash":built.graph.graph_hash,
 "node_count":len(built.graph.nodes),
 "edge_count":len(built.graph.edges),
 "conflict_count":len(built.graph.conflicts),
 "policy_id":built.graph.policy_id,
 "policy_version":built.graph.policy_version,
 "completed_at_utc":datetime.now(timezone.utc).isoformat()
}
artifact_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
'@ | & $Python -
  if($LASTEXITCODE -ne 0){ throw "Entity Resolution / Graph qualification failed" }

  $runtime=Get-Content $artifactPath -Raw | ConvertFrom-Json
  foreach($name in @("exact_merge_passed","merge_lineage_preserved","type_conflict_explicit","relation_endpoints_resolved","duplicate_edges_deduplicated","dangling_relation_rejected","input_order_independent","policy_version_changes_identity","no_inferred_edges","invalid_policy_rejected")){
    $result[$name]=[bool]$runtime.$name
  }
  $result.passed=$result.toolchain_ready -and $result.regression -and $result.exact_merge_passed -and $result.merge_lineage_preserved -and $result.type_conflict_explicit -and $result.relation_endpoints_resolved -and $result.duplicate_edges_deduplicated -and $result.dangling_relation_rejected -and $result.input_order_independent -and $result.policy_version_changes_identity -and $result.no_inferred_edges -and $result.invalid_policy_rejected
 }
 finally { Pop-Location }
}
catch { $result.error=$_.Exception.Message }
finally { $result.completed_at_utc=(Get-Date).ToUniversalTime().ToString("o") }

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $artifactPath -Encoding UTF8
if(-not $result.passed){
 Write-Host "G7 K6 ENTITY RESOLUTION GRAPH: FAIL"
 $result | ConvertTo-Json -Depth 10
 exit 1
}
Write-Host "G7 K6 ENTITY RESOLUTION GRAPH: PASS"
$result | ConvertTo-Json -Depth 10
Write-Host "Evidence: $artifactPath"
