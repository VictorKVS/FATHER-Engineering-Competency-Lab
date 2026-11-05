import json
from pathlib import Path

from father.core.adaptive_role_router import AdaptiveRoleRouter

BASE=Path(__file__).resolve().parent

def check(name,passed,details,rows):
    rows.append({"name":name,"passed":bool(passed),"details":details})
    print(("PASS" if passed else "FAIL"),name,json.dumps(details,ensure_ascii=False))
    return bool(passed)

def main():
    r=AdaptiveRoleRouter(BASE)
    rows=[]; ok=True

    p=r.plan({"role":"text_analyst","complexity":2,"text":"анализ книги"},gpu_temp_c=70)
    ok &= check("routine_text_analysis_uses_qwen3b",
                p.get("ok") and p.get("selected")=="qwen2.5:3b",p,rows)

    p=r.plan({"role":"text_analyst","complexity":4,"text":"глубокий анализ причин"},gpu_temp_c=70)
    ok &= check("complex_text_analysis_escalates_qwen7b",
                p.get("ok") and p.get("selected")=="qwen2.5:7b",p,rows)

    p=r.plan({"role":"creative_writing","complexity":2,"text":"продолжи сцену"},
             gpu_temp_c=70,allow_unbenchmarked=True,multi_draft=True)
    ok &= check("creative_multidraft_keeps_three_writers",
                p.get("ok") and p.get("writers")==["ministral-3:8b","qwen2.5:7b","qwen2.5:3b"],p,rows)

    p=r.plan({"role":"creative_writing","complexity":2,"text":"продолжи сцену"},gpu_temp_c=70)
    ok &= check("creative_production_still_blocked_before_bench",
                (not p.get("ok")) and p.get("reason")=="role_requires_benchmark",p,rows)

    p=r.plan({"role":"text_analyst","complexity":2,"text":"анализ"},gpu_temp_c=91)
    ok &= check("thermal_gate_blocks_hot_gpu",
                (not p.get("ok")) and p.get("reason")=="thermal_gate",p,rows)

    p=r.plan({"complexity":1,"text":"коротко перепиши фразу"},gpu_temp_c=70)
    ok &= check("simple_task_uses_edge_fast",
                p.get("ok") and p.get("selected")=="llama3.2:1b",p,rows)

    evidence={
      "benchmark":"FATHER ADAPTIVE ROLE ROUTER MVP-02",
      "mode":"SHADOW",
      "production_applied":False,
      "checks":rows
    }
    ev=BASE/"evidence/adaptive_role_router_mvp02.json"
    ev.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT:","PASS" if ok else "FAIL")
    print("EVIDENCE:",ev)
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
