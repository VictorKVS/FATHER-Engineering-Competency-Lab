import json
import re
import time
from pathlib import Path

from father.contracts.types import BrainRequest
from father.core.assembler import AgentAssembler

BASE = Path(__file__).resolve().parent

MODELS = [
    ("deepseek-reasoning", "deepseek-r1:7b"),
    ("qwen-analysis", "qwen2.5:7b"),
    ("qwen-analysis-fast", "qwen2.5:3b"),
]

TASKS = [
    {
      "id":"logic_01",
      "prompt":"У Маши больше книг, чем у Оли. У Оли больше книг, чем у Иры. У кого меньше всего книг? Ответь только именем.",
      "accept":["Ира","иры","Иры"],
    },
    {
      "id":"logic_02",
      "prompt":"Все инженеры умеют читать документацию. Некоторые аналитики — инженеры. Следует ли, что некоторые аналитики умеют читать документацию? Ответь только ДА или НЕТ.",
      "accept":["ДА"],
    },
    {
      "id":"constraint_01",
      "prompt":"Есть 3 задачи A,B,C. A должна быть раньше B. C должна быть раньше A. Какой единственный допустимый порядок? Ответь как C>A>B.",
      "accept":["C>A>B"],
    },
    {
      "id":"math_01",
      "prompt":"Сервис обрабатывает 120 запросов за 4 секунды равномерно. Сколько запросов в секунду? Ответь только числом.",
      "accept":["30"],
    },
    {
      "id":"math_02",
      "prompt":"У задачи вероятность успеха 0.8 за одну независимую попытку. Какова вероятность хотя бы одного успеха за 2 попытки? Ответь десятичной дробью.",
      "accept":["0.96","0,96"],
    },
    {
      "id":"planning_01",
      "prompt":"Есть две модели: A quality=90 latency=5000ms, B quality=82 latency=900ms. Требование quality>=80 и latency<2000ms. Какую выбрать? Ответь только A или B.",
      "accept":["B"],
    },
    {
      "id":"reason_01",
      "prompt":"Если все A являются B, а ни один B не является C, может ли какой-либо A быть C? Ответь только ДА или НЕТ.",
      "accept":["НЕТ","НЕТ."],
    },
    {
      "id":"reason_02",
      "prompt":"Риск = вероятность * ущерб. Сценарий X: 0.2*100. Сценарий Y: 0.5*30. Какой риск выше? Ответь только X или Y.",
      "accept":["X"],
    },
]

def normalize(x):
    return re.sub(r"\s+","",(x or "").strip().upper())

def main():
    assembler=AgentAssembler(BASE)
    rows=[]
    results=[]
    for brain_id, runtime_model in MODELS:
        brain=assembler.brain(brain_id)
        passed=0
        total_latency=0.0
        model_rows=[]
        print(f"=== MODEL {brain_id} / {runtime_model} ===")
        for task in TASKS:
            req=BrainRequest(messages=[{"role":"user","content":task["prompt"]}],temperature=0.0,max_tokens=120)
            t0=time.perf_counter()
            resp=brain.generate(req)
            latency=round((time.perf_counter()-t0)*1000,2)
            total_latency+=latency
            out=(resp.content or "").strip()
            ok=(not resp.error) and any(normalize(a) in normalize(out) for a in task["accept"])
            passed+=1 if ok else 0
            row={"task_id":task["id"],"passed":ok,"latency_ms":latency,"output":out[:300],"error":resp.error}
            model_rows.append(row)
            print(("PASS" if ok else "FAIL"),task["id"],json.dumps(row,ensure_ascii=False))
        quality=round(passed/len(TASKS)*100.0,2)
        avg_latency=round(total_latency/len(TASKS),2)
        result={"brain_id":brain_id,"runtime_model":runtime_model,"quality":quality,"avg_latency_ms":avg_latency,"tasks":model_rows}
        results.append(result)
        print("SUMMARY",brain_id,json.dumps({"quality":quality,"avg_latency_ms":avg_latency},ensure_ascii=False))

    ranked=sorted(results,key=lambda x:(-x["quality"],x["avg_latency_ms"]))
    winner=ranked[0]
    gate=winner["quality"]>=75.0
    print("=== REASONING ROLE DECISION ===")
    print(("PASS" if gate else "FAIL"),"reasoning_role_has_qualified_winner",json.dumps({"winner":winner["brain_id"],"winner_quality":winner["quality"],"ranking":[{"brain_id":x["brain_id"],"quality":x["quality"],"avg_latency_ms":x["avg_latency_ms"]} for x in ranked]},ensure_ascii=False))

    report={
      "benchmark":"FATHER REASONING ROLE BENCH MVP-09",
      "goal_progress":{"before_percent":85,"target_percent":89},
      "quality_gate":75.0,
      "results":results,
      "winner":winner["brain_id"],
      "winner_runtime_model":winner["runtime_model"],
      "reasoning_role_ready_for_promotion":bool(gate),
    }
    path=BASE/"evidence/reasoning_role_bench_mvp09.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT:","PASS" if gate else "FAIL")
    print("EVIDENCE:",path)
    raise SystemExit(0 if gate else 1)

if __name__=="__main__":
    main()
