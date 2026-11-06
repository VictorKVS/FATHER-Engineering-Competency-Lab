from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
import json
import os
import urllib.parse
import urllib.request
import uuid


@dataclass
class ModelResult:
    model_id: str
    raw_output: str
    parsed_output: dict[str, Any]


class ModelAdapter(Protocol):
    def run(self, context: dict[str, Any]) -> ModelResult: ...


class ReferenceStage000Adapter:
    """Deterministic Stage 000 reference implementation used to prove the conveyor."""

    model_id = "FATHER_REFERENCE_STAGE000_V1"

    def run(self, context: dict[str, Any]) -> ModelResult:
        src = context["input"]
        idea = str(src.get("raw_idea", "")).strip()
        known_context = src.get("known_context", [])
        constraints = src.get("known_constraints", [])

        facts = []
        if src.get("author_or_sponsor"):
            facts.append({"statement": f"Инициатор указан: {src['author_or_sponsor']}", "source": "input.author_or_sponsor"})
        if known_context:
            facts.append({"statement": "Передан исходный контекст.", "source": "input.known_context"})

        output = {
            "original_idea": idea,
            "normalized_intent": idea,
            "facts": facts,
            "hypotheses": [],
            "assumptions": [],
            "unknowns": [
                "Кто основной пользователь?",
                "Какой измеримый результат считается успехом?",
                "Какие ограничения являются HARD?"
            ],
            "first_questions": [
                "Какую проблему должен решить FATHER?",
                "Кто принимает результат работы?",
                "Какие критерии Stage 000 должны быть проверены до Discovery?"
            ],
            "evidence_refs": ["input.raw_idea"],
            "decision": "START_DISCOVERY" if idea else "NEED_MORE_CONTEXT",
            "constraints": constraints,
        }
        raw = json.dumps(output, ensure_ascii=False, sort_keys=True)
        return ModelResult(self.model_id, raw, output)


class ChatCompletionsHTTPAdapter:
    """Vendor-neutral adapter for local servers exposing /v1/chat/completions."""

    def __init__(self, endpoint: str, model_id: str, timeout: int = 120) -> None:
        self.endpoint = endpoint
        self.model_id = model_id
        self.timeout = timeout

    def run(self, context: dict[str, Any]) -> ModelResult:
        system = (
            "You are executing a FATHER Factory stage. "
            "Use ONLY the supplied context. Return one JSON object and no markdown."
        )
        user = json.dumps(context, ensure_ascii=False)
        payload = {
            "model": self.model_id,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        raw = body["choices"][0]["message"]["content"]
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Model output must be a JSON object")
        return ModelResult(self.model_id, raw, parsed)


class GigaChatRESTAdapter:
    """Native GigaChat REST adapter. Credentials are read only from environment."""

    def __init__(
        self,
        model_id: str = "GigaChat-2-Pro",
        auth_key_env: str = "GIGACHAT_AUTH_KEY",
        scope_env: str = "GIGACHAT_SCOPE",
        timeout: int = 120,
    ) -> None:
        self.model_id = model_id
        self.auth_key_env = auth_key_env
        self.scope_env = scope_env
        self.timeout = timeout

    def _access_token(self) -> str:
        key = os.getenv(self.auth_key_env)
        if not key:
            raise RuntimeError(f"Missing environment secret: {self.auth_key_env}")
        scope = os.getenv(self.scope_env, "GIGACHAT_API_PERS")
        data = urllib.parse.urlencode({"scope": scope}).encode("utf-8")
        req = urllib.request.Request(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(uuid.uuid4()),
                "Authorization": f"Basic {key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        token = body.get("access_token")
        if not token:
            raise RuntimeError("GigaChat OAuth response did not contain access_token")
        return token

    def run(self, context: dict[str, Any]) -> ModelResult:
        token = self._access_token()
        payload = {
            "model": self.model_id,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты исполняешь этап FATHER Factory. "
                        "Используй только переданный контекст. "
                        "Верни один JSON-объект без Markdown."
                    ),
                },
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
            ],
        }
        req = urllib.request.Request(
            "https://api.giga.chat/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        raw = body["choices"][0]["message"]["content"]
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("GigaChat output must be a JSON object")
        return ModelResult(self.model_id, raw, parsed)
