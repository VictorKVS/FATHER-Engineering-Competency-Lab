import json
import os
import shutil
import urllib.request
from pathlib import Path

def ollama_preflight(brains_cfg, min_free_gb=20):
    result={"storage":{},"api":{},"required_models":{},"checks":[]}

    model_root=os.environ.get("OLLAMA_MODELS","").strip()
    storage_path=Path(model_root) if model_root else None
    storage_exists=bool(storage_path and storage_path.exists())
    result["storage"]["path"]=model_root or None
    result["storage"]["exists"]=storage_exists

    free_gb=None
    total_gb=None
    if storage_exists:
        try:
            usage=shutil.disk_usage(storage_path)
            free_gb=round(usage.free/(1024**3),2)
            total_gb=round(usage.total/(1024**3),2)
        except Exception as e:
            result["storage"]["error"]=str(e)

    result["storage"]["free_gb"]=free_gb
    result["storage"]["total_gb"]=total_gb

    result["checks"].append({
        "name":"storage_exists",
        "passed":storage_exists,
        "details":{"path":model_root or None}
    })
    result["checks"].append({
        "name":"storage_free_space",
        "passed":free_gb is not None and free_gb >= float(min_free_gb),
        "details":{"free_gb":free_gb,"min_free_gb":min_free_gb}
    })

    base_urls=sorted(set(v.get("base_url") for v in brains_cfg.values() if v.get("base_url")))
    base_url=base_urls[0] if base_urls else "http://127.0.0.1:11434"
    tags_url=base_url.rstrip("/")+"/api/tags"

    models=[]
    api_ok=False
    api_error=None
    try:
        with urllib.request.urlopen(tags_url,timeout=10) as r:
            payload=json.loads(r.read().decode("utf-8"))
        models=[x.get("name") or x.get("model") for x in payload.get("models",[])]
        models=[x for x in models if x]
        api_ok=True
    except Exception as e:
        api_error=str(e)

    result["api"]={
        "base_url":base_url,
        "tags_url":tags_url,
        "ok":api_ok,
        "model_count":len(models),
        "error":api_error
    }
    result["checks"].append({
        "name":"ollama_api",
        "passed":api_ok,
        "details":result["api"]
    })

    required={v["model"] for v in brains_cfg.values()}
    installed=set(models)
    missing=sorted(required-installed)

    result["required_models"]={
        "required":sorted(required),
        "installed":sorted(installed),
        "missing":missing
    }
    result["checks"].append({
        "name":"required_models_present",
        "passed":api_ok and len(missing)==0,
        "details":result["required_models"]
    })

    result["passed"]=all(c["passed"] for c in result["checks"])
    return result
