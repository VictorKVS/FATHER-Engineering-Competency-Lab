import hashlib
import json

FIELDS=("route","policy","sandbox","tool","agent","knowledge","result","audit_rows")

def digest(value):
    data=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def build_bundle(state,audit_rows):
    result=state.get("result") or {}
    meta=result.get("metadata") or {}
    bundle={
        "run_id":state.get("run_id"),
        "status":state.get("status"),
        "task_type":state.get("task_type"),
        "route":state.get("route"),
        "policy":state.get("policy",[]),
        "sandbox":state.get("sandbox",[]),
        "tool":state.get("tool"),
        "agent":{
            "agent_id":state.get("agent_id"),
            "brain_id":state.get("brain_id"),
            "competency_id":state.get("competency_id")
        },
        "knowledge":{
            "hits":state.get("knowledge_hits",0),
            "sources":meta.get("knowledge_sources",[]),
            "modes":meta.get("knowledge_modes",[])
        },
        "result":{
            "ok":result.get("ok"),
            "content":result.get("content"),
            "model":meta.get("model"),
            "provider":meta.get("provider")
        },
        "audit_rows":audit_rows
    }
    bundle["digests"]={name:digest(bundle[name]) for name in FIELDS}
    bundle["bundle_digest"]=digest(bundle["digests"])
    return bundle

def verify_bundle(bundle):
    expected={name:digest(bundle.get(name)) for name in FIELDS}
    digests_ok=all(bundle.get("digests",{}).get(name)==expected[name] for name in FIELDS)
    bundle_ok=bundle.get("bundle_digest")==digest(bundle.get("digests",{}))
    stages=[row.get("stage") for row in bundle.get("audit_rows",[])]
    trace_ok=all(name in stages for name in ("event","route","policy_agent","assemble","agent","complete"))
    knowledge=bundle.get("knowledge",{})
    source_ok=knowledge.get("hits",0)>0 and bool(knowledge.get("sources"))
    return {
        "ok":bool(digests_ok and bundle_ok and trace_ok and source_ok),
        "digests_ok":digests_ok,
        "bundle_ok":bundle_ok,
        "trace_ok":trace_ok,
        "source_ok":source_ok,
        "stages":stages
    }
