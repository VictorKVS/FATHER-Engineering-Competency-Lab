import base64
import json
import struct
import time
import urllib.request
import zlib
from pathlib import Path

BASE = Path(__file__).resolve().parent
OLLAMA = "http://127.0.0.1:11434/api/generate"

MODELS = [
    ("qwen3-vl-vision", "qwen3-vl:8b-instruct-q4_K_M"),
    ("llava-vision", "llava:7b"),
]

def png_bytes(width, height, pixel_fn):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r,g,b = pixel_fn(x,y)
            raw.extend([r,g,b])
    def chunk(tag,data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)
    return (
        b"\x89PNG\r\n\x1a\n" +
        chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,2,0,0,0)) +
        chunk(b"IDAT",zlib.compress(bytes(raw),9)) +
        chunk(b"IEND",b"")
    )

def make_images():
    # Image A: 3 red blocks on the left, 1 blue block on the right.
    def a(x,y):
        bg=(245,245,245)
        red=(220,40,40); blue=(40,80,220)
        if 10<=x<40 and 10<=y<35: return red
        if 10<=x<40 and 45<=y<70: return red
        if 10<=x<40 and 80<=y<105: return red
        if 100<=x<145 and 35<=y<80: return blue
        return bg

    # Image B: green rectangle above yellow rectangle.
    def b(x,y):
        bg=(250,250,250)
        green=(30,170,70); yellow=(235,205,40)
        if 45<=x<115 and 15<=y<50: return green
        if 45<=x<115 and 75<=y<110: return yellow
        return bg

    return {
        "A": base64.b64encode(png_bytes(160,120,a)).decode("ascii"),
        "B": base64.b64encode(png_bytes(160,120,b)).decode("ascii"),
    }

TASKS = [
    {"id":"count_red","image":"A","prompt":"Сколько красных прямоугольников на изображении? Ответь только числом.","accept":["3"]},
    {"id":"blue_side","image":"A","prompt":"С какой стороны изображения находится синий прямоугольник: слева или справа? Ответь одним словом.","accept":["справа"]},
    {"id":"green_position","image":"B","prompt":"Какой цвет расположен выше: зелёный или жёлтый? Ответь одним словом.","accept":["зелёный","зеленый"]},
    {"id":"yellow_position","image":"B","prompt":"Какой цвет расположен ниже: зелёный или жёлтый? Ответь одним словом.","accept":["жёлтый","желтый"]},
]

def call(model,prompt,image_b64):
    body=json.dumps({
        "model":model,
        "prompt":prompt,
        "images":[image_b64],
        "stream":False,
        "options":{"temperature":0.0,"num_predict":80},
    },ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(OLLAMA,data=body,headers={"Content-Type":"application/json; charset=utf-8"},method="POST")
    t0=time.perf_counter()
    with urllib.request.urlopen(req,timeout=180) as r:
        data=json.loads(r.read().decode("utf-8"))
    return (data.get("response") or "").strip(), round((time.perf_counter()-t0)*1000,2)

def norm(x):
    return (x or "").strip().lower().replace(".","").replace(",","")

def main():
    images=make_images()
    results=[]
    for brain_id,model in MODELS:
        rows=[]; passed=0; total=0.0
        print(f"=== MODEL {brain_id} / {model} ===")
        for task in TASKS:
            try:
                out,latency=call(model,task["prompt"],images[task["image"]])
                ok=any(norm(a) in norm(out) for a in task["accept"])
                err=None
            except Exception as e:
                out=""; latency=0.0; ok=False; err=str(e)
            total+=latency
            passed += 1 if ok else 0
            row={"task_id":task["id"],"passed":ok,"latency_ms":latency,"output":out[:250],"error":err}
            rows.append(row)
            print(("PASS" if ok else "FAIL"),task["id"],json.dumps(row,ensure_ascii=False))
        quality=round(passed/len(TASKS)*100.0,2)
        avg=round(total/len(TASKS),2)
        result={"brain_id":brain_id,"runtime_model":model,"quality":quality,"avg_latency_ms":avg,"tasks":rows}
        results.append(result)
        print("SUMMARY",brain_id,json.dumps({"quality":quality,"avg_latency_ms":avg},ensure_ascii=False))

    ranked=sorted(results,key=lambda x:(-x["quality"],x["avg_latency_ms"]))
    winner=ranked[0]
    gate=winner["quality"]>=75.0
    print("=== VISION ROLE DECISION ===")
    print(("PASS" if gate else "FAIL"),"vision_role_has_qualified_winner",json.dumps({
        "winner":winner["brain_id"],
        "winner_quality":winner["quality"],
        "ranking":[{"brain_id":x["brain_id"],"quality":x["quality"],"avg_latency_ms":x["avg_latency_ms"]} for x in ranked],
    },ensure_ascii=False))

    report={
        "benchmark":"FATHER VISION ROLE BENCH MVP-11",
        "goal_progress":{"before_percent":93,"target_percent":96},
        "quality_gate":75.0,
        "scope":"synthetic color/count/spatial vision qualification",
        "results":results,
        "winner":winner["brain_id"],
        "winner_runtime_model":winner["runtime_model"],
        "vision_role_ready_for_conditional_promotion":bool(gate),
    }
    path=BASE/"evidence/vision_role_bench_mvp11.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RESULT:","PASS" if gate else "FAIL")
    print("EVIDENCE:",path)
    raise SystemExit(0 if gate else 1)

if __name__=="__main__":
    main()
