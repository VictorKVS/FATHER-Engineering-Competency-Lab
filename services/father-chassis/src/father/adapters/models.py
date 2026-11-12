from __future__ import annotations

import json
from urllib.request import Request, urlopen
from father.core.contracts import TraceContext

class GroundedTemplateModel:
    name = "grounded-template-v1"
    def health(self) -> bool: return True
    def generate(self, prompt: str, trace: TraceContext) -> str:
        del trace
        evidence = prompt.split("EVIDENCE:\n",1)[-1].strip()
        return "FATHER answer based on evidence: " + (evidence[:500] if evidence else "NO_EVIDENCE")

class OpenAICompatibleModel:
    """Adapter for local/cloud OpenAI-compatible /v1/chat/completions endpoints."""
    def __init__(self, base_url: str, model: str, api_key: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.name = f"openai-compatible:{model}"
    def health(self) -> bool: return True
    def generate(self, prompt: str, trace: TraceContext) -> str:
        payload = json.dumps({"model": self.model, "messages": [{"role":"user","content":prompt}], "temperature":0}).encode()
        headers = {"Content-Type":"application/json", "X-Father-Trace-Id":trace.trace_id}
        if self.api_key: headers["Authorization"] = f"Bearer {self.api_key}"
        endpoint = self.base_url + ("/chat/completions" if self.base_url.endswith("/v1") else "/v1/chat/completions")
        req = Request(endpoint, data=payload, headers=headers, method="POST")
        with urlopen(req, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
