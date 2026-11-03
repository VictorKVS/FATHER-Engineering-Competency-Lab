import copy
import json
from pathlib import Path

from father.core.preflight import ollama_preflight
from father.core.release_manifest import ReleaseManifest

BASE=Path(__file__).resolve().parent
builder=ReleaseManifest(BASE)

evidence={
    "stage":"FATHER Chassis v2.8 / Stage 19",
    "goal":"prove release manifest and compatibility matrix for verified factory components",
    "checks":[]
}

def add(name,passed,details):
    item={"name":name,"passed":bool(passed),"details":details}
    evidence["checks"].append(item)
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return item

print("=== BUILD RELEASE MANIFEST ===")
manifest=builder.build(
    version="father-controller-2.8-stage19",
    anchor_commit="c5f69c6abc739d8187c3ed293fed7d75a4b28d2a"
)
compat=builder.compatibility(manifest)
digest_check=builder.verify_digest(manifest)

add("release_manifest_built",bool(manifest.get("manifest_digest")),{
    "release_version":manifest["release_version"],
    "chassis_version":manifest["chassis_version"],
    "verified_through_stage":manifest["verified_through_stage"],
    "manifest_digest":manifest["manifest_digest"]
})
add("compatibility_matrix_valid",compat["ok"],compat)
add("release_manifest_digest_valid",digest_check["ok"],digest_check)

print("\n=== RUNTIME PREFLIGHT AGAINST RELEASE ===")
preflight=ollama_preflight(manifest["brains"],min_free_gb=20)
add("release_runtime_preflight",preflight["passed"],{
    "storage":preflight["storage"],
    "api":preflight["api"],
    "required_models":preflight["required_models"]
})

print("\n=== MATRIX COVERAGE ===")
agent_ids={a["agent_id"] for a in manifest["agents"]}
brain_ids=set(manifest["brains"])
routed=set(manifest["routes"]["routes"].values())
routed.add(manifest["routes"]["default_agent_id"])
policy_ids=set(manifest["policies"]["agents"])

add("all_agents_have_brains",
    all(a["brain_id"] in brain_ids for a in manifest["agents"]),
    {
        "agents":sorted(agent_ids),
        "brains":sorted(brain_ids)
    }
)
add("all_routes_resolve",
    routed.issubset(agent_ids),
    {
        "routed_agents":sorted(routed),
        "registered_agents":sorted(agent_ids)
    }
)
add("all_agents_have_policy",
    agent_ids.issubset(policy_ids),
    {
        "agent_ids":sorted(agent_ids),
        "policy_ids":sorted(policy_ids)
    }
)

print("\n=== EXTERNAL ANCHOR INCLUDED ===")
anchor=manifest["external_anchor"]
add("release_contains_external_anchor",
    anchor["commit"]=="c5f69c6abc739d8187c3ed293fed7d75a4b28d2a"
    and bool(anchor["payload"].get("ledger_head_hash")),
    anchor
)

print("\n=== NEGATIVE CONTROL: MISSING BRAIN ===")
bad_brain=copy.deepcopy(manifest)
bad_brain["agents"][0]["brain_id"]="missing-brain-stage19"
bad_brain_check=builder.compatibility(bad_brain)
add("matrix_detects_missing_brain",
    bad_brain_check["ok"] is False
    and any(x.get("kind")=="missing_brain" for x in bad_brain_check["problems"]),
    bad_brain_check
)

print("\n=== NEGATIVE CONTROL: MISSING POLICY ===")
bad_policy=copy.deepcopy(manifest)
victim=bad_policy["agents"][0]["agent_id"]
bad_policy["policies"]["agents"].pop(victim,None)
bad_policy_check=builder.compatibility(bad_policy)
add("matrix_detects_missing_policy",
    bad_policy_check["ok"] is False
    and any(x.get("kind")=="missing_policy" for x in bad_policy_check["problems"]),
    bad_policy_check
)

print("\n=== NEGATIVE CONTROL: MANIFEST MODIFICATION ===")
tampered=copy.deepcopy(manifest)
tampered["release_version"]="tampered-release"
tampered_digest=builder.verify_digest(tampered)
add("manifest_digest_detects_change",
    tampered_digest["ok"] is False,
    tampered_digest
)

release=all(x["passed"] for x in evidence["checks"])
evidence["result"]="PASS" if release else "FAIL"
evidence["compatibility"]=compat
evidence["runtime_preflight"]=preflight

manifest_path=BASE/"evidence/stage19_release_manifest.json"
manifest_path.parent.mkdir(parents=True,exist_ok=True)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")

out=BASE/"evidence/stage19_evidence.json"
out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")

print("\nRESULT:",evidence["result"])
print("EVIDENCE:",out)
print("RELEASE MANIFEST:",manifest_path)
raise SystemExit(0 if release else 1)
