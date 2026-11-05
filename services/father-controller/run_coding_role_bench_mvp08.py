import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
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
    {
        "id": "merge_intervals",
        "prompt": """Напиши функцию Python merge_intervals(intervals).
intervals — список пар [start,end]. Объедини пересекающиеся и соприкасающиеся интервалы.
Порядок входа произвольный. Верни новый список отсортированных интервалов.
Вход не изменяй. Верни только код Python без markdown.""",
        "tests": """
import copy
x=[[5,7],[1,3],[2,4],[8,8]]
orig=copy.deepcopy(x)
assert merge_intervals(x)==[[1,7],[8,8]]
assert x==orig
assert merge_intervals([])==[]
assert merge_intervals([[1,1],[1,2]])==[[1,2]]
""",
    },
    {
        "id": "retry",
        "prompt": """Напиши функцию Python retry_call(fn, attempts, exceptions=(Exception,)).
Она вызывает fn до attempts раз и возвращает результат при успехе.
Повторять только при исключениях из exceptions.
Если все попытки исчерпаны — повторно выбросить последнее исключение.
attempts < 1 -> ValueError.
Верни только код Python без markdown.""",
        "tests": """
state={"n":0}
def flaky():
    state["n"]+=1
    if state["n"]<3:
        raise ValueError("x")
    return 42
assert retry_call(flaky,3,(ValueError,))==42
assert state["n"]==3
try:
    retry_call(lambda:1,0)
except ValueError:
    pass
else:
    raise AssertionError("attempts<1 must fail")
try:
    retry_call(lambda: (_ for _ in ()).throw(TypeError("t")),3,(ValueError,))
except TypeError:
    pass
else:
    raise AssertionError("unexpected exception must propagate")
""",
    },
    {
        "id": "parse_bool",
        "prompt": """Напиши функцию Python parse_bool(value).
Принимает bool или строку.
True-значения: true, yes, 1, on; False-значения: false, no, 0, off.
Строки обрабатывай без учета регистра и с trim пробелов.
Для прочих значений выбрасывай ValueError.
Верни только код Python без markdown.""",
        "tests": """
assert parse_bool(True) is True
assert parse_bool(False) is False
assert parse_bool(" YES ") is True
assert parse_bool("off") is False
for bad in ["maybe",1,None,[]]:
    try:
        parse_bool(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"must reject {bad!r}")
""",
    },
    {
        "id": "redact_secrets",
        "prompt": """Напиши функцию Python redact_secrets(text).
Она должна скрывать значения токенов в строках формата:
password=VALUE
token: VALUE
api_key = VALUE
Имена ключей без учета регистра, пробелы вокруг разделителя допустимы.
Заменяй только VALUE на ***. Остальной текст сохраняй.
Верни только код Python без markdown.""",
        "tests": """
s="user=bob password=hunter2 token: abc123 api_key = XYZ end"
r=redact_secrets(s)
assert "hunter2" not in r and "abc123" not in r and "XYZ" not in r
assert "password=***" in r
assert "token: ***" in r
assert "api_key = ***" in r
assert redact_secrets("nothing here")=="nothing here"
""",
    },
]

TRANSPORT_MARKERS = (
    "Remote end closed connection",
    "WinError 10054",
    "Connection refused",
    "timed out",
)

def ollama_preflight():
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5) as r:
            data=json.loads(r.read().decode("utf-8"))
        return {"ok":True,"models":len(data.get("models",[]))}
    except Exception as e:
        return {"ok":False,"error":str(e)}

def is_transport_error(error):
    text=str(error or "")
    return any(x.lower() in text.lower() for x in TRANSPORT_MARKERS)

def generate_with_retry(brain, req, attempts=3):
    last=None
    total_latency=0.0
    for n in range(1, attempts+1):
        t0=time.perf_counter()
        resp=brain.generate(req)
        elapsed=round((time.perf_counter()-t0)*1000,2)
        total_latency+=elapsed
        last=resp
        if not resp.error:
            return resp, round(total_latency,2), n
        if not is_transport_error(resp.error):
            return resp, round(total_latency,2), n
        time.sleep(2*n)
    return last, round(total_latency,2), attempts

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
    preflight=ollama_preflight()
    print("OLLAMA PREFLIGHT",json.dumps(preflight,ensure_ascii=False))
    if not preflight.get("ok"):
        print("RESULT: INFRA_FAIL")
        print("REASON: ollama_preflight_failed")
        raise SystemExit(2)
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
            resp,latency,retry_count=generate_with_retry(brain,req,attempts=3)
            total_latency+=latency
            code=extract_code(resp.content)
            test=run_tests(code,task["tests"]) if not resp.error else {"passed":False,"stderr":resp.error}
            passed+=1 if test.get("passed") else 0
            row={
                "task_id":task["id"],
                "passed":bool(test.get("passed")),
                "latency_ms":latency,
                "error":resp.error,
                "transport_error":is_transport_error(resp.error),
                "request_attempts":retry_count,
                "stderr":test.get("stderr",""),
                "code_chars":len(code),
            }
            model_rows.append(row)
            print(("PASS" if row["passed"] else "FAIL"),task["id"],json.dumps(row,ensure_ascii=False))
        transport_failures=sum(1 for x in model_rows if x.get("transport_error"))
        if transport_failures>=max(2,len(TASKS)//2):
            print("INFRA_FAIL",brain_id,json.dumps({"transport_failures":transport_failures,"tasks":len(TASKS)},ensure_ascii=False))
            print("RESULT: INFRA_FAIL")
            raise SystemExit(2)
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
    gate_pass=bool(winner["quality"]>=75.0)
    if len(ranked)>1:
        quality_margin=round(winner["quality"]-ranked[1]["quality"],2)
    else:
        quality_margin=winner["quality"]
    qualified=bool(gate_pass)

    print("=== CODING ROLE DECISION ===")
    print("PASS quality_gate" if gate_pass else "FAIL quality_gate",json.dumps({"winner":winner["brain_id"],"winner_quality":winner["quality"],"required":75.0},ensure_ascii=False))
    print(("PASS" if qualified else "FAIL"),"coding_role_has_qualified_winner",json.dumps({"winner":winner["brain_id"],"quality_margin":quality_margin,"ranking":[{"brain_id":x["brain_id"],"quality":x["quality"],"avg_latency_ms":x["avg_latency_ms"]} for x in ranked]},ensure_ascii=False))

    report={
        "benchmark":"FATHER CODING ROLE BENCH MVP-08",
        "goal_progress":{"before_percent":82,"target_percent":86},
        "quality_gate":75.0,
        "results":results,
        "ranking":ranked,
        "winner":winner["brain_id"],
        "coding_role_ready_for_promotion":qualified,
        "winner_runtime_model":winner["runtime_model"],
    }
    path=BASE/"evidence/coding_role_bench_mvp08.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    ok=qualified
    print("RESULT:","PASS" if ok else "FAIL")
    print("EVIDENCE:",path)
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
