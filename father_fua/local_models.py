from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class DiscoveredModel:
    transport: str
    base_url: str
    model_id: str
    local: bool
    healthy: bool
    supports_chat: bool


def _get_json(url: str, timeout: float = 2.0) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def discover_ollama(base_url: str = "http://127.0.0.1:11434") -> list[DiscoveredModel]:
    try:
        data = _get_json(base_url.rstrip("/") + "/api/tags")
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return []
    out: list[DiscoveredModel] = []
    for item in data.get("models", []):
        name = item.get("name")
        if name:
            out.append(DiscoveredModel("OLLAMA", base_url, name, True, True, True))
    return out


def discover_openai_compatible(base_url: str = "http://127.0.0.1:8000/v1") -> list[DiscoveredModel]:
    try:
        data = _get_json(base_url.rstrip("/") + "/models")
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return []
    out: list[DiscoveredModel] = []
    for item in data.get("data", []):
        model_id = item.get("id")
        if model_id:
            out.append(DiscoveredModel("OPENAI_COMPATIBLE", base_url, model_id, True, True, True))
    return out


def discover_local_models() -> list[DiscoveredModel]:
    found = []
    found.extend(discover_ollama())
    for base in (
        "http://127.0.0.1:8000/v1",
        "http://127.0.0.1:1234/v1",
        "http://127.0.0.1:8080/v1",
    ):
        found.extend(discover_openai_compatible(base))
    unique: dict[tuple[str, str, str], DiscoveredModel] = {}
    for model in found:
        unique[(model.transport, model.base_url, model.model_id)] = model
    return list(unique.values())


def ollama_chat(base_url: str, model_id: str, prompt: str, timeout: float = 60.0) -> str:
    payload = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    message = data.get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("empty model response")
    return content


def openai_compatible_chat(base_url: str, model_id: str, prompt: str, timeout: float = 60.0) -> str:
    payload = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("empty model choices")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("empty model response")
    return content


def invoke_model(model: DiscoveredModel, prompt: str, timeout: float = 60.0) -> str:
    if model.transport == "OLLAMA":
        return ollama_chat(model.base_url, model.model_id, prompt, timeout)
    if model.transport == "OPENAI_COMPATIBLE":
        return openai_compatible_chat(model.base_url, model.model_id, prompt, timeout)
    raise ValueError("unsupported model transport")
