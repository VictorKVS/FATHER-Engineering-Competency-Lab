import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE=Path(__file__).resolve().parent
WEB=BASE/"story_bench_review_web"
REPORT=BASE/"evidence/story_model_bench_latest.json"
SCORES=BASE/"evidence/story_model_bench_scores.json"

MIME={".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",".js":"application/javascript; charset=utf-8"}

def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

class H(BaseHTTPRequestHandler):
    def send_data(self,status,body,ctype="application/json; charset=utf-8"):
        if isinstance(body,(dict,list)):
            payload=json.dumps(body,ensure_ascii=False,indent=2).encode("utf-8")
        elif isinstance(body,str):
            payload=body.encode("utf-8")
        else:
            payload=body
        self.send_response(status)
        self.send_header("Content-Type",ctype)
        self.send_header("Content-Length",str(len(payload)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(payload)

    def body(self):
        n=int(self.headers.get("Content-Length","0") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/api/report":
            return self.send_data(200,read_json(REPORT,{"error":"benchmark_report_missing"}))
        if p=="/api/scores":
            return self.send_data(200,read_json(SCORES,{"scores":{},"winner":None}))
        if p=="/":
            p="/index.html"
        target=(WEB/p.lstrip("/")).resolve()
        if WEB.resolve() not in target.parents and target!=WEB.resolve():
            return self.send_data(403,{"error":"forbidden"})
        if not target.exists():
            return self.send_data(404,{"error":"not_found"})
        return self.send_data(200,target.read_bytes(),MIME.get(target.suffix,"application/octet-stream"))

    def do_POST(self):
        p=urlparse(self.path).path
        data=self.body()
        if p=="/api/scores":
            current=read_json(SCORES,{"scores":{},"winner":None})
            current["scores"]=data.get("scores",{})
            current["winner"]=data.get("winner")
            SCORES.parent.mkdir(parents=True,exist_ok=True)
            SCORES.write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding="utf-8")
            return self.send_data(200,{"ok":True,"path":str(SCORES)})
        return self.send_data(404,{"error":"not_found"})

    def log_message(self,fmt,*args):
        print("[STORY-BENCH-REVIEW]",fmt%args)

if __name__=="__main__":
    host="127.0.0.1";port=8092
    print(f"Story Bench Review: http://{host}:{port}")
    ThreadingHTTPServer((host,port),H).serve_forever()
