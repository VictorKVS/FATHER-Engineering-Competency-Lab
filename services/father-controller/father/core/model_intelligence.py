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

    def add_economic_profile(self,model_id,payload):
        m=self.models.get(model_id)
        if not m:
            raise ModelIntelligenceError("unknown model: "+model_id)

        requests_per_month=float(payload.get("requests_per_month",0) or 0)
        human_minutes=float(payload.get("human_minutes_per_task",0) or 0)
        human_hourly_cost=float(payload.get("human_hourly_cost",0) or 0)
        review_minutes=float(payload.get("review_minutes_per_task",0) or 0)

        local_fixed=float(payload.get("local_fixed_monthly_cost",0) or 0)
        local_variable=float(payload.get("local_variable_cost_per_task",0) or 0)
        cloud_variable=float(payload.get("cloud_cost_per_task",0) or 0)
        api_variable=float(payload.get("api_cost_per_task",0) or 0)

        manual_per_task=(human_minutes/60.0)*human_hourly_cost
        review_per_task=(review_minutes/60.0)*human_hourly_cost

        options={
            "local": local_fixed + requests_per_month*(local_variable+review_per_task),
            "cloud": requests_per_month*(cloud_variable+review_per_task),
            "external_api": requests_per_month*(api_variable+review_per_task)
        }
        manual_monthly=requests_per_month*manual_per_task
        savings={k:manual_monthly-v for k,v in options.items()}
        best=min(options,key=options.get) if options else None

        profile={
            "profile_id":payload.get("profile_id") or "profile-"+str(len(m.setdefault("economics",{}).setdefault("profiles",[]))+1).zfill(3),
            "name":payload.get("name","default"),
            "requests_per_month":requests_per_month,
            "human_minutes_per_task":human_minutes,
            "human_hourly_cost":human_hourly_cost,
            "review_minutes_per_task":review_minutes,
            "manual_monthly_cost":round(manual_monthly,2),
            "deployment_monthly_cost":{k:round(v,2) for k,v in options.items()},
            "monthly_savings":{k:round(v,2) for k,v in savings.items()},
            "best_deployment":best,
            "best_monthly_cost":round(options.get(best,0),2) if best else None,
            "best_monthly_saving":round(savings.get(best,0),2) if best else None
        }

        econ=m.setdefault("economics",{"status":"NOT_CALCULATED","profiles":[]})
        econ.setdefault("profiles",[]).append(profile)
        econ["status"]="CALCULATED"
        m["updated_at"]=self._now()
        self.save()
        return deepcopy(profile)

    def set_league_role(self,model_id,task_class,role,score=None):
        if model_id not in self.models:
            raise ModelIntelligenceError("unknown model: "+model_id)
        allowed={"CHAMPION","CHALLENGER","BASELINE","UNRANKED"}
        role=str(role or "").upper()
        if role not in allowed:
            raise ModelIntelligenceError("invalid league role")
        m=self.models[model_id]
        league=m.setdefault("league",{"status":"UNRANKED","role":None})
        roles=league.setdefault("task_classes",{})
        roles[task_class]={
            "role":role,
            "score":score,
            "updated_at":self._now()
        }
        if role!="UNRANKED":
            league["status"]="RANKED"
            league["role"]=role
        m["updated_at"]=self._now()
        self.save()
        return deepcopy(roles[task_class])

    def league(self,task_class):
        rows=[]
        order={"CHAMPION":0,"CHALLENGER":1,"BASELINE":2,"UNRANKED":9}
        for model_id,m in self.models.items():
            info=(m.get("league") or {}).get("task_classes",{}).get(task_class)
            if not info:
                continue
            rows.append({
                "model_id":model_id,
                "role":info.get("role","UNRANKED"),
                "score":info.get("score"),
                "admission_status":m.get("admission_status"),
                "economics":m.get("economics",{})
            })
        return sorted(rows,key=lambda x:(order.get(x["role"],9),-(x["score"] or 0)))

    def application_matrix(self):
        rows=[]
        for model_id,m in self.models.items():
            profiles=(m.get("economics") or {}).get("profiles",[])
            rows.append({
                "model_id":model_id,
                "admission_status":m.get("admission_status"),
                "modalities":m.get("modalities",[]),
                "complexity_range":m.get("complexity_range",[]),
                "resource_class":m.get("resource_class"),
                "latency_class":m.get("latency_class"),
                "deployment":m.get("deployment",[]),
                "commercial_use":m.get("commercial_use"),
                "bench_rank":(m.get("benchmark_evidence") or {}).get("stage24_rank"),
                "quality":(m.get("benchmark_evidence") or {}).get("stage24_avg_quality"),
                "latency_ms":(m.get("benchmark_evidence") or {}).get("stage24_avg_latency_ms"),
                "economics_profiles":len(profiles),
                "best_deployment":profiles[-1].get("best_deployment") if profiles else None,
                "best_monthly_cost":profiles[-1].get("best_monthly_cost") if profiles else None,
                "best_monthly_saving":profiles[-1].get("best_monthly_saving") if profiles else None
            })
        return sorted(rows,key=lambda x:x["model_id"])

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
