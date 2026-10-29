from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
import json
import urllib.request


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


class OpenAICompatibleHTTPAdapter:
    """Adapter for local servers exposing /v1/chat/completions (llama.cpp, Ollama proxy, etc.)."""

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
