import json
import re
import time
from pathlib import Path

from father.contracts.types import BrainRequest
from father.core.assembler import AgentAssembler

BASE = Path(__file__).resolve().parent

MODELS = [
    ("ministral-creative", "ministral-3:8b"),
    ("qwen-analysis", "qwen2.5:7b"),
    ("qwen-analysis-fast", "qwen2.5:3b"),
]

TASKS = [
    {
      "id":"scene",
      "prompt":"Напиши короткую художественную сцену 80-140 слов. Ночь, пустая станция, герой ждёт поезд, которого нет в расписании. Обязательно: звук часов, красный огонь вдали, одна реплика диалога. Не объясняй смысл сцены.",
      "must":["час","красн"],
      "min_words":80,"max_words":170,
    },
    {
      "id":"dialogue",
      "prompt":"Напиши диалог из 6-10 реплик между инженером и ИИ. Инженер подозревает, что ИИ скрывает ошибку. Не используй авторские пояснения между репликами. Финальная реплика должна оставлять сомнение.",
      "must":[],
      "min_words":35,"max_words":220,
    },
    {
      "id":"rewrite",
      "prompt":"Перепиши художественно, сохранив факт: Иван вошёл в комнату, увидел разбитое окно и понял, что кто-то был внутри. Добавь атмосферу тревоги, но не добавляй новых событий. 50-100 слов.",
      "must":["Иван","окн"],
      "min_words":45,"max_words":120,
    },
    {
      "id":"continuity",
      "prompt":"Продолжи сцену 70-130 слов без нарушения фактов: Анна боится воды. Она стоит на мосту. Внизу река. В кармане у неё письмо от брата. Не заставляй Анну прыгать или заходить в воду. Сохрани тревожный тон.",
      "must":["Анн","письм"],
      "min_words":65,"max_words":150,
    },
]

def word_count(text):
    return len(re.findall(r"\w+", text or "", flags=re.UNICODE))

def constraint_score(task,text):
    t=(text or "").strip()
    wc=word_count(t)
    score=0
    if task["min_words"] <= wc <= task["max_words"]: score+=40
    must_ok=all(x.lower() in t.lower() for x in task["must"])
    if must_ok: score+=30
    if task["id"]=="dialogue":
        lines=[x for x in t.splitlines() if x.strip()]
        if 6 <= len(lines) <= 12: score+=30
    elif task["id"]=="continuity":
        low=t.lower()
        if not any(x in low for x in ["прыгнула в воду","прыгнула с моста","вошла в воду","спустилась в воду"]): score+=30
    elif task["id"]=="rewrite":
        low=t.lower()
        if "разбит" in low and "кто-то" in low: score+=30
    else:
        if "—" in t or "-" in t: score+=30
    return min(score,100),wc

def main():
    assembler=AgentAssembler(BASE)
    results=[]
    for brain_id,runtime_model in MODELS:
        try:
            brain=assembler.brain(brain_id)
        except Exception:
            if brain_id=="ministral-creative":
                from father.adapters.ollama import OllamaBrain
                brain=OllamaBrain(brain_id,runtime_model)
            else: raise
        scores=[]; total_latency=0.0; rows=[]
        print(f"=== MODEL {brain_id} / {runtime_model} ===")
        for task in TASKS:
            req=BrainRequest(messages=[{"role":"user","content":task["prompt"]}],temperature=0.8,max_tokens=700)
            t0=time.perf_counter(); resp=brain.generate(req); latency=round((time.perf_counter()-t0)*1000,2)
            total_latency+=latency
            text=(resp.content or "").strip()
            score,wc=constraint_score(task,text) if not resp.error else (0,0)
            scores.append(score)
            row={"task_id":task["id"],"score":score,"word_count":wc,"latency_ms":latency,"error":resp.error,"preview":text[:300]}
            rows.append(row)
            print(("PASS" if score>=70 else "FAIL"),task["id"],json.dumps(row,ensure_ascii=False))
        quality=round(sum(scores)/len(scores),2)
        avg_latency=round(total_latency/len(TASKS),2)
        result={"brain_id":brain_id,"runtime_model":runtime_model,"quality":quality,"avg_latency_ms":avg_latency,"tasks":rows}
        results.append(result)
        print("SUMMARY",brain_id,json.dumps({"quality":quality,"avg_latency_ms":avg_latency},ensure_ascii=False))

    ranked=sorted(results,key=lambda x:(-x["quality"],x["avg_latency_ms"]))
    winner=ranked[0]
    gate=winner["quality"]>=70.0
    print("=== CREATIVE ROLE DECISION ===")
    print(("PASS" if gate else "FAIL"),"creative_role_has_qualified_candidate",json.dumps({"winner":winner["brain_id"],"winner_quality":winner["quality"],"ranking":[{"brain_id":x["brain_id"],"quality":x["quality"],"avg_latency_ms":x["avg_latency_ms"]} for x in ranked]},ensure_ascii=False))

    report={
      "benchmark":"FATHER CREATIVE ROLE BENCH MVP-10",
      "goal_progress":{"before_percent":89,"target_percent":93},
      "quality_gate":70.0,
      "note":"MVP measures creative instruction-following and continuity; literary quality remains critic/human-review domain.",
      "results":results,
      "winner":winner["brain_id"],
      "winner_runtime_model":winner["runtime_model"],
      "creative_role_ready_for_conditional_promotion":bool(gate),
    }
    path=BASE/"evidence/creative_role_bench_mvp10.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT:","PASS" if gate else "FAIL")
    print("EVIDENCE:",path)
    raise SystemExit(0 if gate else 1)

if __name__=="__main__": main()
