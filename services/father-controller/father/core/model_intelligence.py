import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

class ModelIntelligenceError(RuntimeError):
    pass

class ModelIntelligenceRegistry:
    def __init__(self,path):
        self.path=Path(path)
        self.data=json.loads(self.path.read_text(encoding="utf-8"))
        self.models=self.data.setdefault("models",{})

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def save(self):
        self.path.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding="utf-8")

    def list(self):
        rows=[]
        for model_id,m in self.models.items():
            rows.append({
                "model_id":model_id,
                "runtime_model":m.get("runtime_model"),
                "provider":m.get("provider"),
                "lifecycle":m.get("lifecycle"),
                "admission_status":m.get("admission_status"),
                "installed":m.get("installed",False),
                "deployment":m.get("deployment",[]),
                "commercial_use":m.get("commercial_use"),
                "license":m.get("license"),
                "modalities":m.get("modalities",[]),
                "complexity_range":m.get("complexity_range",[]),
                "resource_class":m.get("resource_class"),
                "latency_class":m.get("latency_class"),
                "claim_count":len(m.get("claims",[])),
                "verification":self.verification_summary(model_id)
            })
        return sorted(rows,key=lambda x:x["model_id"])

    def get(self,model_id):
        if model_id not in self.models:
            raise ModelIntelligenceError("unknown model: "+model_id)
        return deepcopy(self.models[model_id])

    def create_candidate(self,payload):
        model_id=str(payload.get("model_id","")).strip()
        if not model_id:
            raise ModelIntelligenceError("model_id is required")
        if model_id in self.models:
            raise ModelIntelligenceError("model already exists: "+model_id)
        now=self._now()
        rec={
            "model_id":model_id,
            "provider":payload.get("provider","unknown"),
            "runtime_model":payload.get("runtime_model") or model_id,
            "version":payload.get("version","unknown"),
            "lifecycle":"candidate",
            "admission_status":"DISCOVERED",
            "installed":bool(payload.get("installed",False)),
            "deployment":payload.get("deployment",[]),
            "commercial_use":"UNVERIFIED",
            "license":{"value":"UNVERIFIED","status":"UNVERIFIED"},
            "modalities":payload.get("modalities",["text"]),
            "strengths":[],
            "weaknesses":[],
            "complexity_range":[],
            "context_window_tokens":None,
            "latency_class":"unknown",
            "resource_class":"unknown",
            "benchmark_evidence":{},
            "economics":{"status":"NOT_CALCULATED","profiles":[]},
            "league":{"status":"UNRANKED","role":None},
            "claims":[],
            "created_at":now,
            "updated_at":now
        }
        self.models[model_id]=rec
        self.save()
        return deepcopy(rec)

    def add_claim(self,model_id,payload):
        m=self.models.get(model_id)
        if not m:
            raise ModelIntelligenceError("unknown model: "+model_id)
        field=str(payload.get("field","")).strip()
        if not field:
            raise ModelIntelligenceError("field is required")
        claims=m.setdefault("claims",[])
        claim={
            "claim_id":"claim-"+str(len(claims)+1).zfill(4),
            "field":field,
            "value":payload.get("value"),
            "source_url":payload.get("source_url"),
            "source_class":payload.get("source_class","OFFICIAL_PRIMARY"),
            "confidence":payload.get("confidence","UNVERIFIED"),
            "verification_status":payload.get("verification_status","UNVERIFIED"),
            "retrieved_at":payload.get("retrieved_at") or self._now(),
            "notes":payload.get("notes","")
        }
        claims.append(claim)
        m["updated_at"]=self._now()

        # Critical normalized fields are promoted only when explicitly confirmed/measured.
        if claim["verification_status"] in {"SOURCE_CONFIRMED","FATHER_MEASURED"}:
            if field=="license":
                m["license"]={"value":claim["value"],"status":claim["verification_status"]}
            elif field=="commercial_use":
                m["commercial_use"]=claim["value"]
            elif field=="context_window_tokens":
                try:m["context_window_tokens"]=int(claim["value"])
                except Exception:pass
            elif field=="resource_class":
                m["resource_class"]=claim["value"]
            elif field=="latency_class":
                m["latency_class"]=claim["value"]
            elif field=="deployment":
                m["deployment"]=claim["value"] if isinstance(claim["value"],list) else [claim["value"]]

        self._recompute_admission(model_id)
        self.save()
        return deepcopy(claim)

    def set_claim_status(self,model_id,claim_id,status,confidence=None):
        m=self.models.get(model_id)
        if not m:
            raise ModelIntelligenceError("unknown model: "+model_id)
        allowed=set(self.data.get("verification_statuses",[]))
        if status not in allowed:
            raise ModelIntelligenceError("invalid verification status")
        for claim in m.get("claims",[]):
            if claim.get("claim_id")==claim_id:
                claim["verification_status"]=status
                if confidence:
                    claim["confidence"]=confidence
                m["updated_at"]=self._now()
                self._recompute_admission(model_id)
                self.save()
                return deepcopy(claim)
        raise ModelIntelligenceError("claim not found: "+claim_id)

    def verification_summary(self,model_id):
        m=self.models[model_id]
        claims=m.get("claims",[])
        by_status={}
        critical={"license","commercial_use","context_window_tokens","deployment","pricing"}
        critical_confirmed=set()
        conflicts=[]
        for c in claims:
            st=c.get("verification_status","UNVERIFIED")
            by_status[st]=by_status.get(st,0)+1
            if c.get("field") in critical and st in {"SOURCE_CONFIRMED","FATHER_MEASURED"}:
                critical_confirmed.add(c.get("field"))
            if st=="CONFLICT":
                conflicts.append(c.get("field"))
        return {
            "claims":len(claims),
            "by_status":by_status,
            "critical_confirmed":sorted(critical_confirmed),
            "conflicts":sorted(set(conflicts)),
            "bench_ready":len(conflicts)==0 and {"license","commercial_use","deployment"}.issubset(critical_confirmed)
        }

    def _recompute_admission(self,model_id):
        m=self.models[model_id]
        summary=self.verification_summary(model_id)
        if summary["conflicts"]:
            m["admission_status"]="DATA_COLLECTION"
        elif summary["bench_ready"]:
            if m.get("admission_status") not in {"CHALLENGER","APPROVED_LOCAL","APPROVED_CONDITIONAL","REJECTED","DEPRECATED"}:
                m["admission_status"]="READY_FOR_BENCH"
        elif m.get("claims"):
            m["admission_status"]="DATA_COLLECTION"
        else:
            m["admission_status"]="DISCOVERED"

    def set_admission(self,model_id,status):
        allowed=set(self.data.get("admission_statuses",[]))
        if status not in allowed:
            raise ModelIntelligenceError("invalid admission status")
        if model_id not in self.models:
            raise ModelIntelligenceError("unknown model: "+model_id)
        self.models[model_id]["admission_status"]=status
        self.models[model_id]["updated_at"]=self._now()
        self.save()
        return self.get(model_id)

    def health(self):
        problems=[]
        for model_id,m in self.models.items():
            if m.get("model_id")!=model_id:
                problems.append({"kind":"id_mismatch","model_id":model_id})
            if "claims" not in m:
                problems.append({"kind":"missing_claims","model_id":model_id})
        return {
            "ok":not problems,
            "models":len(self.models),
            "problems":problems
        }
