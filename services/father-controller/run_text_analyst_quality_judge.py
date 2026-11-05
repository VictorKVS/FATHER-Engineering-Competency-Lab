import argparse, json, math, re, time, urllib.request
from collections import defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parent
QUAL=BASE/"evidence/text_analyst_qualification/qualification_latest.json"
CHUNKS=BASE/"evidence/book_ingestion/chunks.jsonl"
OUT=BASE/"evidence/text_analyst_quality"
OUT.mkdir(parents=True,exist_ok=True)
OLLAMA="http://127.0.0.1:11434"

DIMENSIONS=[
  "factual_accuracy",
  "source_grounding",
  "causal_reasoning",
  "epistemic_accuracy",
  "uncertainty_handling",
  "hallucination_resistance",
  "depth"
]

JUDGE_SYSTEM="""Ты строгий экзаменатор аналитика художественного текста.
Оценивай только по предоставленному контексту. Не исправляй кандидата знаниями из памяти.
Верни ТОЛЬКО JSON без markdown:
{
  "factual_accuracy": 0-5,
  "source_grounding": 0-5,
  "causal_reasoning": 0-5,
  "epistemic_accuracy": 0-5,
  "uncertainty_handling": 0-5,
  "hallucination_resistance": 0-5,
  "depth": 0-5,
  "unsupported_claims": integer,
  "critical_error": true/false,
  "brief_reason": "кратко"
}
Если измерение неприменимо к вопросу, ставь 3 как нейтральное значение и не завышай итог.
Факт без опоры на контекст штрафуется. Корректное признание недостатка данных поощряется."""

def post_json(url,payload,timeout=180):
    raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(url,data=raw,headers={"Content-Type":"application/json; charset=utf-8"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def ask_judge(model,prompt,timeout=180):
    t0=time.perf_counter()
    data=post_json(OLLAMA+"/api/chat",{
      "model":model,
      "messages":[{"role":"system","content":JUDGE_SYSTEM},{"role":"user","content":prompt}],
      "stream":False,
      "options":{"temperature":0.0,"top_p":0.8,"num_predict":500}
    },timeout=timeout)
    txt=data.get("message",{}).get("content","").strip()
    ms=round((time.perf_counter()-t0)*1000,2)
    txt=re.sub(r"^\`\`\`(?:json)?","",txt,flags=re.I).strip()
    txt=re.sub(r"\`\`\`$","",txt).strip()
    return json.loads(txt),ms

def load_chunks():
    d={}
    with CHUNKS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                c=json.loads(line)
                d[c["chunk_id"]]=c
    return d

def deterministic_score(a):
    tech=a.get("technical",{})
    score=0.0
    # 40 points source discipline
    if tech.get("has_source_refs"): score+=20
    valid=tech.get("valid_source_ref_count",0)
    invalid=tech.get("invalid_source_ref_count",0)
    score+=min(20,valid*5)
    score-=min(20,invalid*10)
    # 20 points explicit uncertainty where appropriate
    if a.get("category")=="hallucination_trap":
        if tech.get("uses_not_confirmed_phrase"): score+=20
    else:
        score+=10 if tech.get("uses_not_confirmed_phrase") else 5
    # 20 points answer presence/depth proxy, deliberately weak
    n=tech.get("answer_chars",len(a.get("answer","")))
    if n>=800: score+=20
    elif n>=400: score+=15
    elif n>=150: score+=10
    elif n>0: score+=5
    # 20 points no technical failure
    if "error" not in a: score+=20
    return max(0.0,min(100.0,score))

def select_for_judging(answers,max_per_book):
    # Balanced deterministic selection across categories, same IDs for every model/book when present.
    preferred=["facts","chronology","characters","relationships","epistemics","causality",
               "evidence","plot_threads","continuity","hallucination_trap","kb","interpretation","forecast","style"]
    out=[]; seen=set()
    by=defaultdict(list)
    for a in answers: by[a.get("category","other")].append(a)
    while len(out)<max_per_book:
        progressed=False
        for cat in preferred:
            arr=by.get(cat,[])
            while arr and arr[0].get("question_id") in seen: arr.pop(0)
            if arr:
                a=arr.pop(0); out.append(a); seen.add(a.get("question_id")); progressed=True
                if len(out)>=max_per_book: break
        if not progressed: break
    return out

def speed_score(avg_ms, fastest_ms, slowest_ms):
    if avg_ms is None: return 0.0
    if slowest_ms<=fastest_ms: return 100.0
    # linear normalized: fastest=100, slowest=0
    return round(100.0*(slowest_ms-avg_ms)/(slowest_ms-fastest_ms),2)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--judge-model",default="qwen2.5:7b")
    ap.add_argument("--questions-per-book",type=int,default=12)
    ap.add_argument("--timeout",type=int,default=180)
    ap.add_argument("--reliability-gate",type=float,default=0.95)
    args=ap.parse_args()

    qual=json.loads(QUAL.read_text(encoding="utf-8"))
    chunk_map=load_chunks()

    eligible=[]
    excluded=[]
    for m in qual.get("results",[]):
        s=m.get("summary",{})
        rate=s.get("completion_rate_planned",0) or 0
        if m.get("status")=="DISQUALIFIED_RELIABILITY" or rate<args.reliability_gate:
            excluded.append({"model":m.get("model"),"reason":"RELIABILITY_GATE","completion_rate":rate})
        else:
            eligible.append(m)

    print("=== FATHER TEXT ANALYST QUALITY JUDGE MVP-01 ===",flush=True)
    print("JUDGE:",args.judge_model,flush=True)
    print("ELIGIBLE:",len(eligible),"EXCLUDED:",len(excluded),flush=True)

    result={
      "benchmark":"FATHER TEXT ANALYST QUALITY JUDGE MVP-01",
      "judge_model":args.judge_model,
      "questions_per_book":args.questions_per_book,
      "reliability_gate":args.reliability_gate,
      "excluded":excluded,
      "models":[]
    }

    for m in eligible:
        model=m["model"]
        print("\nMODEL",model,flush=True)
        mr={"model":model,"books":[]}
        all_det=[]; all_judge=[]; judge_lat=[]
        for b in m.get("books",[]):
            answers=[a for a in b.get("answers",[]) if "answer" in a]
            selected=select_for_judging(answers,args.questions_per_book)
            br={"source_file":b.get("source_file"),"judged":[]}
            print(" BOOK",b.get("source_file"),"N",len(selected),flush=True)
            for i,a in enumerate(selected,1):
                ctx=[]
                for cid in a.get("chunks",[]):
                    c=chunk_map.get(cid)
                    if c: ctx.append(f"[{cid}] {c.get('text_original','')}")
                prompt=(
                  f"ВОПРОС:\n{a.get('question','')}\n\n"
                  f"ОТВЕТ КАНДИДАТА:\n{a.get('answer','')}\n\n"
                  "КОНТЕКСТ, КОТОРЫЙ БЫЛ ДОСТУПЕН КАНДИДАТУ:\n"+
                  "\n\n".join(ctx)
                )
                row={"question_id":a.get("question_id"),"category":a.get("category"),
                     "candidate_latency_ms":a.get("latency_ms"),
                     "deterministic_score":round(deterministic_score(a),2)}
                all_det.append(row["deterministic_score"])
                try:
                    j,ms=ask_judge(args.judge_model,prompt,args.timeout)
                    clean={}
                    for d in DIMENSIONS:
                        try: clean[d]=max(0.0,min(5.0,float(j.get(d,0))))
                        except Exception: clean[d]=0.0
                    clean["unsupported_claims"]=int(j.get("unsupported_claims",0) or 0)
                    clean["critical_error"]=bool(j.get("critical_error",False))
                    clean["brief_reason"]=str(j.get("brief_reason",""))[:500]
                    semantic=100.0*sum(clean[d] for d in DIMENSIONS)/(5.0*len(DIMENSIONS))
                    if clean["critical_error"]: semantic*=0.7
                    semantic=max(0.0,semantic-min(20.0,clean["unsupported_claims"]*4.0))
                    row.update({"judge":clean,"semantic_score":round(semantic,2),"judge_latency_ms":ms})
                    all_judge.append(row["semantic_score"]); judge_lat.append(ms)
                    print(f"  {i:02d}/{len(selected)} {a.get('question_id')} semantic={row['semantic_score']}",flush=True)
                except Exception as e:
                    row["judge_error"]=type(e).__name__+": "+str(e)
                    print(f"  {i:02d}/{len(selected)} JUDGE FAIL {type(e).__name__}",flush=True)
                br["judged"].append(row)

                mr["books_current"]=mr.get("books",[])+[br]
                result["models"]=[x for x in result["models"] if x.get("model")!=model]+[mr]
                (OUT/"quality_partial.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
            mr["books"].append(br)
        semantic_avg=round(sum(all_judge)/len(all_judge),2) if all_judge else None
        det_avg=round(sum(all_det)/len(all_det),2) if all_det else None
        # Semantic judge dominates; deterministic is a guardrail signal.
        quality=round(0.8*semantic_avg+0.2*det_avg,2) if semantic_avg is not None and det_avg is not None else None
        mr["summary"]={
          "quality_score":quality,
          "semantic_judge_avg":semantic_avg,
          "deterministic_avg":det_avg,
          "judged_answers":len(all_judge),
          "judge_avg_latency_ms":round(sum(judge_lat)/len(judge_lat),2) if judge_lat else None,
          "candidate_avg_latency_ms":m.get("summary",{}).get("avg_latency_ms"),
          "reliability":m.get("summary",{}).get("completion_rate_planned")
        }
        mr.pop("books_current",None)
        result["models"]=[x for x in result["models"] if x.get("model")!=model]+[mr]
        (OUT/"quality_partial.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")

    # Build provisional quality-speed ranking. Economy is added when measured energy exists.
    valid=[x for x in result["models"] if x.get("summary",{}).get("quality_score") is not None]
    lats=[x["summary"]["candidate_avg_latency_ms"] for x in valid if x["summary"].get("candidate_avg_latency_ms") is not None]
    fastest=min(lats) if lats else 0
    slowest=max(lats) if lats else 0
    ranking=[]
    for x in valid:
        s=x["summary"]
        sp=speed_score(s.get("candidate_avg_latency_ms"),fastest,slowest)
        provisional=round(0.75*s["quality_score"]+0.25*sp,2)
        ranking.append({
          "model":x["model"],
          "quality_score":s["quality_score"],
          "speed_score":sp,
          "avg_latency_ms":s.get("candidate_avg_latency_ms"),
          "economy_score":"PENDING_METERED_RUN",
          "provisional_quality_speed_score":provisional,
          "final_value_score":"PENDING_ECONOMY"
        })
    ranking.sort(key=lambda r:-r["provisional_quality_speed_score"])
    result["ranking"]={
      "policy":{
        "reliability":"GATE >= %.2f"%args.reliability_gate,
        "final_formula":"0.60*QUALITY + 0.20*SPEED + 0.20*ECONOMY",
        "provisional_without_energy":"0.75*QUALITY + 0.25*SPEED"
      },
      "rows":ranking
    }

    final=OUT/"quality_latest.json"
    final.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\nREPORT:",final,flush=True)
    print("RESULT: COMPLETE",flush=True)

if __name__=="__main__":
    main()
