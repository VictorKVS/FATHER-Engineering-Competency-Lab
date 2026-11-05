import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from father.contracts.types import BrainRequest
from father.core.assembler import AgentAssembler

BASE = Path(__file__).resolve().parent

MODELS = [
    ("qwen-coder", "qwen2.5-coder:7b-instruct-q4_K_M"),
    ("qwen-analysis", "qwen2.5:7b"),
    ("qwen-analysis-fast", "qwen2.5:3b"),
]

TASKS = [
    {
        "id": "aggregate",
        "prompt": """Напиши функцию Python aggregate_orders(rows).
rows — список словарей с полями user, amount, status.
Учитывай только status == "paid".
Верни словарь user -> сумма amount.
amount может быть int или float.
Не изменяй входные данные.
Верни только код Python без markdown.""" ,
        "tests": """
import copy
rows=[{"user":"a","amount":10,"status":"paid"},{"user":"a","amount":2.5,"status":"paid"},{"user":"b","amount":7,"status":"cancelled"},{"user":"b","amount":3,"status":"paid"}]
orig=copy.deepcopy(rows)
assert aggregate_orders(rows)=={"a":12.5,"b":3}
assert rows==orig
assert aggregate_orders([])=={}
""",
    },
    {
        "id": "dedupe",
        "prompt": """Напиши функцию Python dedupe_keep_order(items).
Она удаляет дубликаты, сохраняет порядок первого появления и должна работать для hashable значений.
Пример: [3,1,3,2,1] -> [3,1,2].
Верни только код Python без markdown.""" ,
        "tests": """
assert dedupe_keep_order([3,1,3,2,1])==[3,1,2]
assert dedupe_keep_order([])==[]
assert dedupe_keep_order(["a","a","b"])==["a","b"]
""",
    },
    {
        "id": "safe_divide",
        "prompt": """Исправь функцию и верни только корректный код Python без markdown.
Требования: safe_divide(a,b) возвращает a/b; при b==0 возвращает None; не подавляет другие ошибки.
Исходник:
def safe_divide(a,b):
    try:
        return a/b
    except Exception:
        return None
""",
        "tests": """
assert safe_divide(10,2)==5
assert safe_divide(1,0) is None
try:
    safe_divide("x",2)
except TypeError:
    pass
else:
    raise AssertionError("TypeError must not be swallowed")
""",
    },
    {
        "id": "path_guard",
        "prompt": """Напиши функцию Python safe_child_path(base, user_path).
Она должна вернуть абсолютный pathlib.Path внутри base.
Если user_path через .. или абсолютный путь выходит за пределы base — выбросить ValueError.
Разрешай нормальные вложенные пути.
Верни только код Python без markdown.""" ,
        "tests": """
from pathlib import Path
import tempfile
with tempfile.TemporaryDirectory() as d:
    base=Path(d)
    p=safe_child_path(base,"a/b.txt")
    assert p==base.resolve()/"a"/"b.txt"
    try:
        safe_child_path(base,"../escape.txt")
    except ValueError:
        pass
    else:
        raise AssertionError("traversal must be blocked")
    try:
        safe_child_path(base, str((base.parent/"outside.txt").resolve()))
    except ValueError:
        pass
    else:
        raise AssertionError("absolute escape must be blocked")
""",
    },
]

def extract_code(text):
    raw=(text or "").strip()
    m=re.search(r"```(?:python)?\s*(.*?)```",raw,re.S|re.I)
    return (m.group(1) if m else raw).strip()

def run_tests(code, tests):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"candidate.py"
        p.write_text(code+"\n\n"+tests,encoding="utf-8")
        try:
            cp=subprocess.run([sys.executable,str(p)],capture_output=True,text=True,timeout=8)
            return {
                "passed": cp.returncode==0,
                "returncode": cp.returncode,
                "stdout": cp.stdout[-1000:],
                "stderr": cp.stderr[-1500:],
            }
        except subprocess.TimeoutExpired:
            return {"passed":False,"returncode":None,"stdout":"","stderr":"TIMEOUT"}

def main():
    assembler=AgentAssembler(BASE)
    results=[]
    for brain_id, runtime_model in MODELS:
        brain=assembler.brain(brain_id)
        passed=0
        total_latency=0.0
        model_rows=[]
        print(f"=== MODEL {brain_id} / {runtime_model} ===")
        for task in TASKS:
            req=BrainRequest(
                messages=[{"role":"user","content":task["prompt"]}],
                temperature=0.0,
                max_tokens=900,
            )
            t0=time.perf_counter()
            resp=brain.generate(req)
            latency=round((time.perf_counter()-t0)*1000,2)
            total_latency+=latency
            code=extract_code(resp.content)
            test=run_tests(code,task["tests"]) if not resp.error else {"passed":False,"stderr":resp.error}
            passed+=1 if test.get("passed") else 0
            row={
                "task_id":task["id"],
                "passed":bool(test.get("passed")),
                "latency_ms":latency,
                "error":resp.error,
                "stderr":test.get("stderr",""),
                "code_chars":len(code),
            }
            model_rows.append(row)
            print(("PASS" if row["passed"] else "FAIL"),task["id"],json.dumps(row,ensure_ascii=False))
        quality=round(passed/len(TASKS)*100.0,2)
        avg_latency=round(total_latency/len(TASKS),2)
        results.append({
            "brain_id":brain_id,
            "runtime_model":runtime_model,
            "passed":passed,
            "total":len(TASKS),
            "quality":quality,
            "avg_latency_ms":avg_latency,
            "tasks":model_rows,
        })
        print("SUMMARY",brain_id,json.dumps({"quality":quality,"avg_latency_ms":avg_latency},ensure_ascii=False))

    ranked=sorted(results,key=lambda x:(-x["quality"],x["avg_latency_ms"]))
    winner=ranked[0]
    coder=next(x for x in results if x["brain_id"]=="qwen-coder")
    gate_pass=bool(coder["quality"]>=75.0)
    promoted=bool(gate_pass and winner["brain_id"]=="qwen-coder")

    print("=== CODING ROLE DECISION ===")
    print("PASS quality_gate" if gate_pass else "FAIL quality_gate",json.dumps({"coder_quality":coder["quality"],"required":75.0},ensure_ascii=False))
    print(("PASS" if promoted else "FAIL"),"qwen_coder_wins_role",json.dumps({"winner":winner["brain_id"],"ranking":[{"brain_id":x["brain_id"],"quality":x["quality"],"avg_latency_ms":x["avg_latency_ms"]} for x in ranked]},ensure_ascii=False))

    report={
        "benchmark":"FATHER CODING ROLE BENCH MVP-08",
        "goal_progress":{"before_percent":82,"target_percent":86},
        "quality_gate":75.0,
        "results":results,
        "ranking":ranked,
        "winner":winner["brain_id"],
        "coding_role_ready_for_promotion":promoted,
    }
    path=BASE/"evidence/coding_role_bench_mvp08.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    ok=promoted
    print("RESULT:","PASS" if ok else "FAIL")
    print("EVIDENCE:",path)
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
