from __future__ import annotations

import http.client
import json
from dataclasses import dataclass
from urllib.parse import urlparse


LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


@dataclass(frozen=True)
class DiscoveredModel:
    transport: str
    base_url: str
    model_id: str
    local: bool
    healthy: bool
    supports_chat: bool


def _parse_loopback_http(base_url: str) -> tuple[str, int, str]:
    parsed = urlparse(base_url)
    if parsed.scheme != "http":
        raise ValueError("only loopback http transport is allowed")
    if parsed.hostname not in LOOPBACK_HOSTS:
        raise ValueError("only loopback model endpoints are allowed")
    port = parsed.port or 80
    prefix = parsed.path.rstrip("/")
    return parsed.hostname, port, prefix


def _request_json(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    timeout: float = 2.0,
) -> dict:
    host, port, prefix = _parse_loopback_http(base_url)
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"

    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        conn.request(method, prefix + path, body=body, headers=headers)
        resp = conn.getresponse()
        if resp.status < 200 or resp.status >= 300:
            raise RuntimeError(f"model endpoint HTTP {resp.status}")
        raw = resp.read().decode("utf-8")
        return json.loads(raw)
    finally:
        conn.close()


def discover_ollama(base_url: str = "http://127.0.0.1:11434") -> list[DiscoveredModel]:
    try:
        data = _request_json(base_url, "/api/tags")
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
        return []
    out: list[DiscoveredModel] = []
    for item in data.get("models", []):
        name = item.get("name")
        if name:
            out.append(DiscoveredModel("OLLAMA", base_url, name, True, True, True))
    return out


def discover_openai_compatible(base_url: str = "http://127.0.0.1:8000/v1") -> list[DiscoveredModel]:
    try:
        data = _request_json(base_url, "/models")
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
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
    data = _request_json(
        base_url,
        "/api/chat",
        method="POST",
        payload={
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=timeout,
    )
    content = data.get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("empty model response")
    return content


def openai_compatible_chat(base_url: str, model_id: str, prompt: str, timeout: float = 60.0) -> str:
    data = _request_json(
        base_url,
        "/chat/completions",
        method="POST",
        payload={
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        },
        timeout=timeout,
    )
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("empty model choices")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("empty model response")
    return content


def invoke_model(model: DiscoveredModel, prompt: str, timeout: float = 60.0) -> str:
    _parse_loopback_http(model.base_url)
    if model.transport == "OLLAMA":
        return ollama_chat(model.base_url, model.model_id, prompt, timeout)
    if model.transport == "OPENAI_COMPATIBLE":
        return openai_compatible_chat(model.base_url, model.model_id, prompt, timeout)
    raise ValueError("unsupported model transport")
