from __future__ import annotations
from dataclasses import dataclass

from father_fua.local_models import DiscoveredModel


@dataclass(frozen=True)
class ModelCompatibilityResult:
    status: str
    reasons: tuple[str, ...]


def evaluate_local_model(
    model: DiscoveredModel,
    *,
    prompt_chars: int,
    require_chat: bool = True,
    require_local: bool = True,
    max_prompt_chars: int = 24000,
) -> ModelCompatibilityResult:
    reasons: list[str] = []

    if require_local and not model.local:
        reasons.append("model is not local")
    if not model.healthy:
        reasons.append("model is not healthy")
    if require_chat and not model.supports_chat:
        reasons.append("chat capability missing")
    if model.transport not in {"OLLAMA", "OPENAI_COMPATIBLE"}:
        reasons.append("unsupported transport")
    if prompt_chars <= 0:
        reasons.append("empty prompt")
    if prompt_chars > max_prompt_chars:
        reasons.append("prompt exceeds compatibility limit")

    return ModelCompatibilityResult(
        status="PASS" if not reasons else "DENY",
        reasons=tuple(reasons),
    )
