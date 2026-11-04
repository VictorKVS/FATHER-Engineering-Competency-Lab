import json
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE=Path(__file__).resolve().parent
WEB=BASE/"story_studio_web"
OLLAMA_URL="http://127.0.0.1:11434/api/chat"
MODEL="qwen2.5:7b"

SYSTEM_PROMPT="""Ты FATHER Story Agent — профессиональный соавтор художественных рассказов.
Работай свободно и выразительно: сохраняй характеры, атмосферу, ритм, лексику и причинно-следственные связи.
Не морализируй и не вставляй предупреждения без необходимости.
Учитывай все уточнения пользователя как редакторские требования к текущему тексту.
Режимы:
CONTINUE — продолжай историю органично, не пересказывая уже написанное.
REWRITE — переработай текст, сохраняя сюжетное ядро, но улучшая язык, драматургию и связность.
SIMILAR — создай новый фрагмент в сходной манере, атмосфере и структуре, но не копируй формулировки.
EDIT — внеси конкретные изменения из уточнения пользователя.
Возвращай только художественный результат, без служебных комментариев, если пользователь явно не просит объяснение."""

MIME={
    ".html":"text/html; charset=utf-8",
    ".css":"text/css; charset=utf-8",
    ".js":"application/javascript; charset=utf-8"
}

def ollama_chat(messages,temperature=0.9):
    payload=json.dumps({
        "model":MODEL,
        "messages":messages,
        "stream":False,
        "options":{"temperature":temperature,"top_p":0.95}
    },ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type":"application/json; charset=utf-8"}
    )
    with urllib.request.urlopen(req,timeout=300) as r:
        data=json.loads(r.read().decode("utf-8"))
    return data.get("message",{}).get("content","")

class Handler(BaseHTTPRequestHandler):
    def send_data(self,status,body,ctype="application/json; charset=utf-8"):
        if isinstance(body,(dict,list)):
            payload=json.dumps(body,ensure_ascii=False).encode("utf-8")
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

    def json_body(self):
        n=int(self.headers.get("Content-Length","0") or 0)
        raw=self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/api/health":
            return self.send_data(200,{"status":"ok","service":"father-story-agent","model":MODEL,"single_llm":True})
        if p=="/":
            p="/index.html"
        target=(WEB/p.lstrip("/")).resolve()
        if WEB.resolve() not in target.parents and target!=WEB.resolve():
            return self.send_data(403,{"error":"forbidden"})
        if not target.exists() or not target.is_file():
            return self.send_data(404,{"error":"not_found"})
        return self.send_data(200,target.read_bytes(),MIME.get(target.suffix,"application/octet-stream"))

    def do_POST(self):
        p=urlparse(self.path).path
        try:
            data=self.json_body()
            if p!="/api/story":
                return self.send_data(404,{"error":"not_found"})
            text=str(data.get("text","")).strip()
            instruction=str(data.get("instruction","")).strip()
            mode=str(data.get("mode","CONTINUE")).upper()
            history=data.get("history") or []
            if not text:
                return self.send_data(400,{"error":"text_required"})
            mode_prompt={
                "CONTINUE":"Продолжи этот текст.",
                "REWRITE":"Переработай этот текст, сохранив сюжетное ядро.",
                "SIMILAR":"Создай новый фрагмент в похожей манере и атмосфере.",
                "EDIT":"Отредактируй текст по уточнению пользователя."
            }.get(mode,"Продолжи этот текст.")
            user_content=f"""РЕЖИМ: {mode}
ЗАДАЧА: {mode_prompt}
УТОЧНЕНИЕ: {instruction or 'нет дополнительных уточнений'}

ИСХОДНЫЙ ТЕКСТ:
{text}"""
            messages=[{"role":"system","content":SYSTEM_PROMPT}]
            for item in history[-8:]:
                role=item.get("role")
                if role in ("user","assistant"):
                    messages.append({"role":role,"content":str(item.get("content",""))})
            messages.append({"role":"user","content":user_content})
            out=ollama_chat(messages,float(data.get("temperature",0.9)))
            return self.send_data(200,{
                "ok":True,
                "agent_id":"father-story-agent",
                "brain_id":"qwen-analysis",
                "runtime_model":MODEL,
                "mode":mode,
                "content":out
            })
        except Exception as e:
            return self.send_data(400,{"error":type(e).__name__,"message":str(e)})

    def log_message(self,fmt,*args):
        print("[STORY-STUDIO]",fmt%args)

if __name__=="__main__":
    host="127.0.0.1"; port=8091
    print(f"FATHER Story Studio: http://{host}:{port}")
    print(f"Single LLM: {MODEL}")
    ThreadingHTTPServer((host,port),Handler).serve_forever()
