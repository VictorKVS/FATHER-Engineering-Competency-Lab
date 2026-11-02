import json, time, urllib.request
from father.core.brain import BrainAdapter
from father.contracts.types import BrainResponse

class OllamaBrain(BrainAdapter):
    def __init__(self, brain_id, model, base_url="http://127.0.0.1:11434"):
        self.brain_id=brain_id; self.model=model; self.base_url=base_url.rstrip("/")

    def health(self):
        try:
            with urllib.request.urlopen(self.base_url+"/api/tags",timeout=5) as r:
                data=json.loads(r.read().decode("utf-8"))
            return {"status":"ok","models":len(data.get("models",[]))}
        except Exception as e:
            return {"status":"error","error":str(e)}

    def capabilities(self):
        return {"chat":True,"text":True,"provider":"ollama"}

    def generate(self, request):
        prompt="\n".join(f'{m.get("role","user")}: {m.get("content","")}' for m in request.messages)
        body={"model":self.model,"prompt":prompt,"stream":False,
              "options":{"temperature":request.temperature,"num_predict":request.max_tokens}}
        raw=json.dumps(body,ensure_ascii=False).encode("utf-8")
        req=urllib.request.Request(self.base_url+"/api/generate",data=raw,
            headers={"Content-Type":"application/json; charset=utf-8"},method="POST")
        t0=time.perf_counter()
        try:
            with urllib.request.urlopen(req,timeout=300) as r:
                data=json.loads(r.read().decode("utf-8"))
            return BrainResponse(
                brain_id=self.brain_id,provider="ollama",model=self.model,
                content=data.get("response",""),
                finish_reason="stop" if data.get("done") else None,
                metrics={"elapsed_ms":int((time.perf_counter()-t0)*1000),
                         "prompt_eval_count":data.get("prompt_eval_count"),
                         "eval_count":data.get("eval_count"),
                         "total_duration":data.get("total_duration"),
                         "eval_duration":data.get("eval_duration")}
            )
        except Exception as e:
            return BrainResponse(brain_id=self.brain_id,provider="ollama",
                                 model=self.model,content="",error=str(e))
