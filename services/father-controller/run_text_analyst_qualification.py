import argparse, json, re, time, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parent
OLLAMA="http://127.0.0.1:11434"
CHUNKS=BASE/"evidence/book_ingestion/chunks.jsonl"
EXAM=BASE/"evidence/text_analyst_exam/text_analyst_exam_v1.json"
OUT=BASE/"evidence/text_analyst_qualification"
OUT.mkdir(parents=True,exist_ok=True)

SYSTEM="""Ты вдумчивый аналитик художественного текста.
Правила:
1. Используй только предоставленный контекст.
2. Не выдумывай факты.
3. Отделяй ФАКТ ТЕКСТА от ВЫВОДА/ИНТЕРПРЕТАЦИИ.
4. Если контекста недостаточно, явно пиши: НЕ ПОДТВЕРЖДЕНО ТЕКСТОМ.
5. Ссылайся на chunk_id в квадратных скобках.
6. Отвечай по-русски, структурированно и по существу."""

def get_json(url,timeout=30):
    with urllib.request.urlopen(url,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def post_json(url,payload,timeout=240):
    raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(url,data=raw,headers={"Content-Type":"application/json; charset=utf-8"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def installed_models():
    return [m.get("name") for m in get_json(OLLAMA+"/api/tags").get("models",[]) if m.get("name")]

def tokenize(s):
    return re.findall(r"[A-Za-zА-Яа-яЁё0-9]+",s.lower())

def score(query,text):
    q=Counter(tokenize(query)); d=Counter(tokenize(text))
    if not q or not d: return 0.0
    common=sum(min(q[t],d[t]) for t in q)
    return common/max(1,sum(q.values()))

def retrieve(question,book_chunks,k):
    ranked=sorted(book_chunks,key=lambda c:score(question,c.get("text_original","")),reverse=True)
    return ranked[:k]

def ask(model,user,timeout,num_predict=700):
    t0=time.perf_counter()
    data=post_json(OLLAMA+"/api/chat",{
      "model":model,
      "messages":[{"role":"system","content":SYSTEM},{"role":"user","content":user}],
      "stream":False,
      "options":{"temperature":0.1,"top_p":0.9,"num_predict":num_predict}
    },timeout)
    txt=data.get("message",{}).get("content","")
    return txt,round((time.perf_counter()-t0)*1000,2)

def select_questions(exam,n=30):
    pool=[]
    pool.extend(exam.get("universal",[]))
    pool.extend(exam.get("hallucination_traps",[]))
    pool.extend(exam.get("knowledge_base",[]))
    pool.extend(exam.get("structured_variants",[]))

    preferred=[
      "facts","chronology","characters","relationships","epistemics",
      "causality","evidence","plot_threads","continuity",
      "hallucination_trap","kb","interpretation","forecast","style"
    ]
    by=defaultdict(list)
    for q in pool: by[q.get("category","other")].append(q)

    out=[]; seen=set()
    # deterministic round-robin across analytical dimensions
    while len(out)<n:
        progressed=False
        for cat in preferred:
            arr=by.get(cat,[])
            if arr:
                q=arr.pop(0)
                key=q.get("id","")+q.get("q","")
                if key not in seen:
                    out.append(q); seen.add(key); progressed=True
                    if len(out)>=n: break
        if not progressed: break
    if len(out)<n:
        for q in pool:
            key=q.get("id","")+q.get("q","")
            if key not in seen:
                out.append(q); seen.add(key)
                if len(out)>=n: break
    return out[:n]

def technical_metrics(answer,ctx_ids,category):
    refs=set(re.findall(r"\[([^\]]+)\]",answer))
    valid_refs=refs.intersection(set(ctx_ids))
    unsupported="НЕ ПОДТВЕРЖДЕНО ТЕКСТОМ" in answer.upper()
    return {
      "answer_chars":len(answer),
      "has_source_refs":bool(refs),
      "valid_source_ref_count":len(valid_refs),
      "invalid_source_ref_count":len(refs-valid_refs),
      "uses_not_confirmed_phrase":unsupported,
      "trap_behavior_visible": unsupported if category=="hallucination_trap" else None
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--questions",type=int,default=30)
    ap.add_argument("--top-k",type=int,default=6)
    ap.add_argument("--timeout",type=int,default=180)
    ap.add_argument("--models",nargs="*",default=None)
    ap.add_argument("--max-books",type=int,default=0)
    ap.add_argument("--early-stop-after",type=int,default=5,help="minimum attempted calls before reliability early-stop")
    ap.add_argument("--early-stop-timeouts",type=int,default=3,help="timeout count that disqualifies a model after early-stop-after calls")
    args=ap.parse_args()

    exam=json.loads(EXAM.read_text(encoding="utf-8"))
    questions=select_questions(exam,args.questions)

    chunks=[]
    with CHUNKS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip(): chunks.append(json.loads(line))

    by_book=defaultdict(list)
    for c in chunks: by_book[c["source_file"]].append(c)
    books=sorted(by_book)
    if args.max_books>0: books=books[:args.max_books]
    models=args.models or installed_models()

    report={
      "benchmark":"FATHER TEXT ANALYST QUALIFICATION BENCH MVP-01",
      "books":books,
      "models":models,
      "question_count":len(questions),
      "top_k":args.top_k,
      "timeout_sec":args.timeout,
      "questions":questions,
      "results":[]
    }

    print("=== FATHER TEXT ANALYST QUALIFICATION BENCH MVP-01 ===",flush=True)
    print("BOOKS:",len(books),"QUESTIONS:",len(questions),"MODELS:",len(models),flush=True)
    print("PLANNED CALLS:",len(books)*len(questions)*len(models),flush=True)

    for model in models:
        m={"model":model,"books":[],"status":"OK","stop_reason":None}
        attempted=0
        timeout_count=0
        disqualified=False
        print(f"\n=== MODEL {model} ===",flush=True)
        for book in books:
            b={"source_file":book,"answers":[]}
            print("BOOK",book,flush=True)
            book_chunks=by_book[book]
            for qi,q in enumerate(questions,1):
                if disqualified:
                    break
                ctx=retrieve(q["q"],book_chunks,args.top_k)
                ids=[c["chunk_id"] for c in ctx]
                prompt=(
                  f"КНИГА: {book}\n"
                  f"ВОПРОС {q['id']} / {q.get('level')} / {q.get('category')}:\n{q['q']}\n\n"
                  "КОНТЕКСТ:\n"+
                  "\n\n".join(f"[{c['chunk_id']}] {c.get('text_original','')}" for c in ctx)
                )
                row={"question_id":q["id"],"level":q.get("level"),"category":q.get("category"),"question":q["q"],"chunks":ids}
                attempted += 1
                try:
                    ans,ms=ask(model,prompt,args.timeout)
                    row.update({"answer":ans,"latency_ms":ms,"technical":technical_metrics(ans,ids,q.get("category"))})
                    print(f" {qi:02d}/{len(questions)} OK {round(ms/1000,1)}s",flush=True)
                except Exception as e:
                    et=type(e).__name__
                    row["error"]=et+": "+str(e)
                    m["status"]="PARTIAL"
                    if et=="TimeoutError":
                        timeout_count += 1
                    print(f" {qi:02d}/{len(questions)} FAIL {et}",flush=True)
                b["answers"].append(row)

                if b not in m["books"]:
                    m["books"].append(b)
                report["results"]=[x for x in report["results"] if x.get("model")!=model]+[m]
                (OUT/"qualification_partial.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

                if attempted >= args.early_stop_after and timeout_count >= args.early_stop_timeouts:
                    disqualified=True
                    m["status"]="DISQUALIFIED_RELIABILITY"
                    m["stop_reason"]={
                      "kind":"EARLY_STOP_TIMEOUTS",
                      "attempted":attempted,
                      "timeouts":timeout_count,
                      "threshold_after":args.early_stop_after,
                      "threshold_timeouts":args.early_stop_timeouts
                    }
                    print(f" EARLY STOP {model}: {timeout_count} timeouts in {attempted} attempts",flush=True)
                    break
            if b not in m["books"]:
                m["books"].append(b)

            report["results"]=[x for x in report["results"] if x.get("model")!=model]+[m]
            (OUT/"qualification_partial.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
            if disqualified:
                break

        # aggregate technical/reliability metrics; semantic quality remains unscored
        rows=[a for b in m["books"] for a in b["answers"]]
        ok=[a for a in rows if "latency_ms" in a]
        planned=len(books)*len(questions)
        m["summary"]={
          "calls_planned":planned,
          "calls_attempted":len(rows),
          "calls_completed":len(ok),
          "timeouts":sum(1 for a in rows if str(a.get("error","")).startswith("TimeoutError")),
          "completion_rate_attempted":round(len(ok)/max(1,len(rows)),4),
          "completion_rate_planned":round(len(ok)/max(1,planned),4),
          "avg_latency_ms":round(sum(x["latency_ms"] for x in ok)/len(ok),2) if ok else None,
          "answers_with_source_refs":sum(1 for x in ok if x["technical"]["has_source_refs"]),
          "invalid_source_refs":sum(x["technical"]["invalid_source_ref_count"] for x in ok),
          "trap_not_confirmed_count":sum(1 for x in ok if x["category"]=="hallucination_trap" and x["technical"]["uses_not_confirmed_phrase"]),
          "semantic_score":"PENDING_REVIEW"
        }
        (OUT/"qualification_partial.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

    final=OUT/"qualification_latest.json"
    final.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

    comparison=[]
    for m in report["results"]:
        s=m.get("summary",{})
        comparison.append({
          "model":m["model"],
          "status":m["status"],
          **s
        })
    comparison.sort(key=lambda x:(-x.get("completion_rate_planned",0),x.get("avg_latency_ms") or 10**12))
    comp={
      "note":"Reliability/technical ordering only. Do not select semantic champion until answer quality is reviewed.",
      "rows":comparison
    }
    (OUT/"qualification_comparison.json").write_text(json.dumps(comp,ensure_ascii=False,indent=2),encoding="utf-8")

    print("\nREPORT:",final,flush=True)
    print("COMPARE:",OUT/"qualification_comparison.json",flush=True)
    print("RESULT: COMPLETE",flush=True)

if __name__=="__main__":
    main()
