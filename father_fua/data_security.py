from __future__ import annotations

import re
from dataclasses import dataclass


SECRET_PATTERNS = (
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*\S+"),
    re.compile(r"(?i)secret\s*[:=]\s*\S+"),
    re.compile(r"(?i)password\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]+=*"),
)


@dataclass(frozen=True)
class DataInspection:
    classification: str
    secret_like: bool
    reasons: tuple[str, ...]


def inspect_text(text: str) -> DataInspection:
    if not isinstance(text, str):
        raise TypeError("text must be string")
    if len(text) > 1_000_000:
        raise ValueError("input too large")

    reasons: list[str] = []
    secret_like = False

    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            secret_like = True
            reasons.append("credential-like pattern detected")
            break

    classification = "CREDENTIAL" if secret_like else "INTERNAL"
    return DataInspection(classification, secret_like, tuple(reasons))


def remote_model_allowed(text: str) -> bool:
    inspection = inspect_text(text)
    return not inspection.secret_like


def redact_secrets(text: str) -> str:
    result = text
    for pattern in SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result
