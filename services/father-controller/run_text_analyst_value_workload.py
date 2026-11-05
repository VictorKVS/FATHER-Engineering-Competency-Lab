import argparse, json, re, time, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parent
OLLAMA="http://127.0.0.1:11434"
CHUNKS=BASE/"evidence/book_ingestion/chunks.jsonl"
EXAM=BASE/"evidence/text_analyst_exam/text_analyst_exam_v1.json"
OUT=BASE/"evidence/text_analyst_value"
OUT.mkdir(parents=True,exist_ok=True)

SYSTEM="""Ты аналитик художественного текста.
Используй только предоставленный контекст.
Не выдумывай факты.
Если данных недостаточно, пиши НЕ ПОДТВЕРЖДЕНО ТЕКСТОМ.
Ссылайся на chunk_id в квадратных скобках.
Отвечай по-русски."""

def post_json(url,payload,timeout=180):
    raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(url,data=raw,headers={"Content-Type":"application/json; charset=utf-8"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def tok(s): return re.findall(r"[A-Za-zА-Яа-яЁё0-9]+",s.lower())
def lex(q,t):
    a=Counter(tok(q)); b=Counter(tok(t))
    if not a: return 0
    return sum(min(a[k],b[k]) for k in a)/max(1,sum(a.values()))

def select(exam,n):
    pool=[]
    for k in ["universal","hallucination_traps","knowledge_base","structured_variants"]:
        pool.extend(exam.get(k,[]))
    preferred=["facts","chronology","characters","relationships","epistemics","causality",
               "evidence","plot_threads","continuity","hallucination_trap","kb","interpretation","forecast","style"]
    by=defaultdict(list)
    for q in pool: by[q.get("category","other")].append(q)
    out=[]; seen=set()
    while len(out)<n:
        progressed=False
        for c in preferred:
            if by[c]:
                q=by[c].pop(0)
                if q["id"] not in seen:
                    out.append(q); seen.add(q["id"]); progressed=True
                    if len(out)>=n: break
        if not progressed: break
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",required=True)
    ap.add_argument("--questions",type=int,default=12)
    ap.add_argument("--top-k",type=int,default=6)
    ap.add_argument("--timeout",type=int,default=180)
    args=ap.parse_args()

    exam=json.loads(EXAM.read_text(encoding="utf-8"))
    qs=select(exam,args.questions)
    chunks=[]
    with CHUNKS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip(): chunks.append(json.loads(line))
    # Fixed corpus for fair economy comparison: first book used in qualification.
    book=sorted({c["source_file"] for c in chunks})[0]
    bc=[c for c in chunks if c["source_file"]==book]

    rows=[]
    print("=== FATHER VALUE WORKLOAD ===",flush=True)
    print("MODEL:",args.model,"BOOK:",book,"QUESTIONS:",len(qs),flush=True)
    for i,q in enumerate(qs,1):
        ctx=sorted(bc,key=lambda c:lex(q["q"],c.get("text_original","")),reverse=True)[:args.top_k]
        prompt=f"КНИГА: {book}\nВОПРОС: {q['q']}\n\nКОНТЕКСТ:\n"+"\n\n".join(
            f"[{c['chunk_id']}] {c.get('text_original','')}" for c in ctx)
        t0=time.perf_counter()
        row={"question_id":q["id"],"category":q.get("category")}
        try:
            d=post_json(OLLAMA+"/api/chat",{
              "model":args.model,
              "messages":[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],
              "stream":False,
              "options":{"temperature":0.1,"top_p":0.9,"num_predict":700}
            },args.timeout)
            ans=d.get("message",{}).get("content","")
            ms=round((time.perf_counter()-t0)*1000,2)
            row.update({"latency_ms":ms,"answer_chars":len(ans)})
            print(f"{i:02d}/{len(qs)} OK {ms/1000:.1f}s",flush=True)
        except Exception as e:
            row["error"]=type(e).__name__+": "+str(e)
            print(f"{i:02d}/{len(qs)} FAIL {type(e).__name__}",flush=True)
        rows.append(row)

    ok=[r for r in rows if "latency_ms" in r]
    safe=re.sub(r"[^A-Za-z0-9_.-]+","_",args.model)
    out=OUT/f"value_workload_{safe}.json"
    data={
      "model":args.model,"book":book,"questions":len(qs),
      "completed":len(ok),
      "completion_rate":round(len(ok)/max(1,len(rows)),4),
      "avg_latency_ms":round(sum(r["latency_ms"] for r in ok)/len(ok),2) if ok else None,
      "rows":rows
    }
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print("REPORT:",out,flush=True)
    print("RESULT: COMPLETE" if len(ok)==len(rows) else "RESULT: PARTIAL",flush=True)

if __name__=="__main__":
    main()
