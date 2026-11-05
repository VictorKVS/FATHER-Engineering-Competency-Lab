import json
from pathlib import Path
from father.core.role_model_router import RoleModelRouter

BASE=Path(__file__).resolve().parent

def main():
    r=RoleModelRouter(BASE)
    checks=[]

    analyst=r.choose("text_analyst")
    checks.append(("text_analyst_prefers_qwen3b",
                   analyst.get("ok") and analyst.get("preferred")=="qwen2.5:3b",
                   analyst))

    creative=r.choose("creative_writing")
    checks.append(("creative_not_auto_promoted_before_bench",
                   (not creative.get("ok")) and creative.get("reason")=="role_requires_benchmark",
                   creative))

    creative_exp=r.choose("creative_writing",allow_unbenchmarked=True)
    checks.append(("creative_keeps_ministral_candidate",
                   creative_exp.get("preferred")=="ministral-3:8b",
                   creative_exp))

    unknown=r.choose("missing-role")
    checks.append(("unknown_role_blocked",not unknown.get("ok"),unknown))

    out={"benchmark":"FATHER ROLE MODEL MATRIX MVP-01","checks":[]}
    ok=True
    for name,passed,details in checks:
        ok=ok and passed
        out["checks"].append({"name":name,"passed":passed,"details":details})
        print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))

    ev=BASE/"evidence/role_model_matrix_mvp01.json"
    ev.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT:","PASS" if ok else "FAIL")
    print("EVIDENCE:",ev)
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
