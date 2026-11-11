from __future__ import annotations
import json
import urllib.request
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelProbe:
    base_url: str
    model: str
    reachable: bool
    advertised_models: tuple[str, ...]
    selected_present: bool
    error: str | None = None

def probe_openai_compatible(base_url: str, model: str, timeout: float = 5.0) -> ModelProbe:
    url = base_url.rstrip("/") + "/models"
    try:
        req = urllib.request.Request(url, headers={"Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode("utf-8"))
        models = tuple(
            str(item.get("id"))
            for item in payload.get("data", [])
            if isinstance(item, dict) and item.get("id")
        )
        return ModelProbe(
            base_url=base_url,
            model=model,
            reachable=True,
            advertised_models=models,
            selected_present=(model in models if model else bool(models)),
        )
    except Exception as exc:
        return ModelProbe(
            base_url=base_url,
            model=model,
            reachable=False,
            advertised_models=(),
            selected_present=False,
            error=f"{type(exc).__name__}: {exc}",
        )
