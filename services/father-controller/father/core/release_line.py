import hashlib
import json
from copy import deepcopy
from pathlib import Path

class ReleaseError(RuntimeError):
    pass

class PrimitiveReleaseLine:
    def __init__(self,base_dir):
        self.base=Path(base_dir)
        self.releases=self.base/"releases"
        self.releases.mkdir(parents=True,exist_ok=True)

    def _sha256_text(self,text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _write_json(self,path,data):
        payload=json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)
        path.write_text(payload,encoding="utf-8")
        return {
            "file":path.name,
            "sha256":self._sha256_text(payload),
            "bytes":len(payload.encode("utf-8"))
        }

    def release(self,spec,bench_result,build_report=None,model_selection=None,release_id=None):
        product_id=spec.get("product_id","unknown-product")
        rid=release_id or (product_id+"-r1")
        target=self.releases/rid

        if bench_result.get("status")!="READY":
            return {
                "released":False,
                "status":"BLOCKED",
                "release_id":rid,
                "path":str(target),
                "reason":"acceptance_gate_not_ready"
            }

        if target.exists():
            raise ReleaseError("release already exists: "+str(target))

        target.mkdir(parents=True,exist_ok=False)

        artifacts=[]
        artifacts.append(self._write_json(target/"product_spec.json",spec))
        artifacts.append(self._write_json(target/"bench_report.json",bench_result))
        artifacts.append(self._write_json(target/"build_report.json",build_report or {}))
        artifacts.append(self._write_json(target/"model_selection.json",model_selection or {}))

        manifest={
            "release_schema":"1.0",
            "release_id":rid,
            "product_id":product_id,
            "status":"READY",
            "artifacts":artifacts
        }
        manifest_meta=self._write_json(target/"release_manifest.json",manifest)

        ready={
            "release_id":rid,
            "product_id":product_id,
            "status":"READY",
            "manifest_sha256":manifest_meta["sha256"]
        }
        self._write_json(target/"READY.json",ready)

        return {
            "released":True,
            "status":"READY",
            "release_id":rid,
            "path":str(target),
            "manifest":manifest,
            "manifest_sha256":manifest_meta["sha256"]
        }

    def verify(self,release_id):
        target=self.releases/release_id
        problems=[]
        if not target.exists():
            return {"ok":False,"problems":[{"kind":"release_missing","release_id":release_id}]}

        manifest_path=target/"release_manifest.json"
        ready_path=target/"READY.json"
        if not manifest_path.exists():
            problems.append({"kind":"manifest_missing"})
            return {"ok":False,"problems":problems}
        if not ready_path.exists():
            problems.append({"kind":"ready_marker_missing"})

        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest.get("artifacts",[]):
            p=target/item["file"]
            if not p.exists():
                problems.append({"kind":"artifact_missing","file":item["file"]})
                continue
            text=p.read_text(encoding="utf-8")
            actual=self._sha256_text(text)
            if actual!=item["sha256"]:
                problems.append({
                    "kind":"artifact_hash_mismatch",
                    "file":item["file"],
                    "expected":item["sha256"],
                    "actual":actual
                })

        return {
            "ok":not problems,
            "release_id":release_id,
            "status":manifest.get("status"),
            "problems":problems
        }
