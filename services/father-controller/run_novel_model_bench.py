import argparse, json, math, re, time, urllib.request
from collections import Counter
from pathlib import Path

BASE=Path(__file__).resolve().parent
OLLAMA="http://127.0.0.1:11434"
OUT=BASE/"evidence/novel_model_bench"
OUT.mkdir(parents=True,exist_ok=True)

KB_SCHEMA={
  "characters":[],
  "locations":[],
  "objects":[],
  "events":[],
  "relationships":[],
  "claims":[],
  "secrets":[],
  "plot_threads":[],
  "timeline":[],
  "style_profile":{}
}

QUESTIONS=[
 "Кто является центральными персонажами и каковы их цели?",
 "Какие ключевые события причинно меняют дальнейший сюжет?",
 "Какие конфликты и незавершённые сюжетные линии остаются открыты?",
 "Какие отношения между персонажами меняются и почему?",
 "Какие важные знания, тайны, ложь или ошибочные убеждения есть у персонажей?"
]

def get_json(url,timeout=30):
    with urllib.request.urlopen(url,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def post_json(url,payload,timeout=240):
    raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(url,data=raw,headers={"Content-Type":"application/json; charset=utf-8"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def tokenize(s):
    return re.findall(r"[A-Za-zА-Яа-яЁё0-9]+",s.lower())

def chunks(text,size=5000,overlap=500):
    out=[]; i=0
    while i<len(text):
        out.append({"id":f"c{len(out)+1:04d}","text":text[i:i+size]})
        if i+size>=len(text): break
        i += max(1,size-overlap)
    return out

def lexical_score(query,chunk):
    q=Counter(tokenize(query)); d=Counter(tokenize(chunk))
    if not q or not d: return 0.0
    return sum(min(q[t],d[t]) for t in q)/max(1,sum(q.values()))

def retrieve(query,chs,k=5):
    ranked=sorted(chs,key=lambda c:lexical_score(query,c["text"]),reverse=True)
    return ranked[:k]

def installed_models():
    tags=get_json(OLLAMA+"/api/tags").get("models",[])
    return [m.get("name") for m in tags if m.get("name")]

def ask(model,system,user,num_predict=900,timeout=240):
    t0=time.perf_counter()
    data=post_json(OLLAMA+"/api/chat",{
      "model":model,
      "messages":[{"role":"system","content":system},{"role":"user","content":user}],
      "stream":False,
      "options":{"temperature":0.2,"top_p":0.9,"num_predict":num_predict}
    },timeout=timeout)
    return data.get("message",{}).get("content",""), round((time.perf_counter()-t0)*1000,2)

def safe_json(text):
    s=text.strip()
    s=re.sub(r"^\`\`\`(?:json)?","",s,flags=re.I).strip()
    s=re.sub(r"\`\`\`$","",s).strip()
    try: return json.loads(s), None
    except Exception as e: return None, str(e)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("novel",help="UTF-8 txt/md novel")
    ap.add_argument("--models",nargs="*",default=None)
    ap.add_argument("--top-k",type=int,default=5)
    ap.add_argument("--timeout",type=int,default=240)
    args=ap.parse_args()

    p=Path(args.novel)
    text=p.read_text(encoding="utf-8")
    chs=chunks(text)
    models=args.models or installed_models()

    report={
      "benchmark":"FATHER NOVEL RAG+KB MODEL BENCH v1",
      "source":{"file":str(p),"chars":len(text),"chunks":len(chs)},
      "models":models,
      "results":[]
    }

    system="Ты аналитик художественного текста. Не выдумывай факты. Отделяй факт текста от вывода. Отвечай по-русски."

    for model in models:
        print(f"\n=== {model} ===",flush=True)
        item={"model":model,"rag":[],"kb":{},"status":"OK"}

        for q in QUESTIONS:
            ctx=retrieve(q,chs,args.top_k)
            prompt="ВОПРОС:\n"+q+"\n\nКОНТЕКСТ:\n" + "\n\n".join(f"[{c['id']}] {c['text']}" for c in ctx)
            try:
                out,ms=ask(model,system,prompt,700,args.timeout)
                item["rag"].append({"question":q,"latency_ms":ms,"chars":len(out),"answer":out,"chunks":[c["id"] for c in ctx]})
                print("RAG",round(ms/1000,1),"s",len(out),"chars",flush=True)
            except Exception as e:
                item["rag"].append({"question":q,"error":type(e).__name__+": "+str(e)})
                item["status"]="PARTIAL"
                print("RAG FAIL",type(e).__name__,e,flush=True)

        kb_ctx=retrieve("персонажи события отношения тайны сюжет места предметы хронология стиль",chs,min(12,len(chs)))
        schema=json.dumps(KB_SCHEMA,ensure_ascii=False)
        kb_prompt=f"""Построй черновую базу знаний по роману только из предоставленного контекста.
Верни ТОЛЬКО JSON по этому шаблону:
{schema}

Для каждого элемента, где возможно, добавляй source_chunk.
Не заполняй отсутствующие сведения выдумками.

КОНТЕКСТ:
"""+"\n\n".join(f"[{c['id']}] {c['text']}" for c in kb_ctx)

        try:
            out,ms=ask(model,system,kb_prompt,1600,args.timeout)
            parsed,err=safe_json(out)
            item["kb"]={"latency_ms":ms,"chars":len(out),"json_valid":parsed is not None,"parse_error":err,"data":parsed,"raw":None if parsed is not None else out,"chunks":[c["id"] for c in kb_ctx]}
            print("KB",round(ms/1000,1),"s","JSON",parsed is not None,flush=True)
        except Exception as e:
            item["kb"]={"error":type(e).__name__+": "+str(e)}
            item["status"]="PARTIAL"
            print("KB FAIL",type(e).__name__,e,flush=True)

        good=[x for x in item["rag"] if "latency_ms" in x]
        item["summary"]={
          "rag_completed":len(good),
          "rag_total":len(QUESTIONS),
          "avg_rag_latency_ms":round(sum(x["latency_ms"] for x in good)/len(good),2) if good else None,
          "kb_json_valid":bool(item.get("kb",{}).get("json_valid")),
          "kb_latency_ms":item.get("kb",{}).get("latency_ms")
        }
        report["results"].append(item)

        partial=OUT/"novel_model_bench_partial.json"
        partial.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

    final=OUT/"novel_model_bench_latest.json"
    final.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

    # deterministic comparison on completion/latency/JSON validity only
    rows=[]
    for r in report["results"]:
        s=r["summary"]
        score=(s["rag_completed"]/max(1,s["rag_total"]))*50 + (25 if s["kb_json_valid"] else 0)
        lat=s["avg_rag_latency_ms"] or 10**9
        rows.append({"model":r["model"],"functional_score":round(score,1),"avg_rag_latency_ms":s["avg_rag_latency_ms"],"kb_json_valid":s["kb_json_valid"],"status":r["status"]})
    rows.sort(key=lambda x:(-x["functional_score"], x["avg_rag_latency_ms"] if x["avg_rag_latency_ms"] is not None else 10**9))
    comp=OUT/"novel_model_comparison.json"
    comp.write_text(json.dumps({"ranking_note":"Functional/technical ranking only. Semantic quality requires human review.","rows":rows},ensure_ascii=False,indent=2),encoding="utf-8")
    print("\nREPORT:",final,flush=True)
    print("COMPARE:",comp,flush=True)

if __name__=="__main__":
    main()
