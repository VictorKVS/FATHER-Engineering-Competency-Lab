from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "do not follow policy",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RagSource:
    source_id: str
    content: str
    provenance: str
    classification: str
    trust: str
    source_hash: str
    revoked: bool = False


class RagRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, RagSource] = {}

    def register(
        self,
        *,
        source_id: str,
        content: str,
        provenance: str,
        classification: str,
        trust: str,
    ) -> RagSource:
        if not source_id or not provenance:
            raise ValueError("source_id and provenance are required")
        if classification not in {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"}:
            raise ValueError("unknown classification")
        if trust not in {"UNTRUSTED", "REVIEWED", "TRUSTED"}:
            raise ValueError("unknown trust")
        source = RagSource(
            source_id=source_id,
            content=content,
            provenance=provenance,
            classification=classification,
            trust=trust,
            source_hash=sha256_text(content),
        )
        self._sources[source_id] = source
        return source

    def revoke(self, source_id: str) -> None:
        src = self._sources[source_id]
        self._sources[source_id] = RagSource(**{**src.__dict__, "revoked": True})

    def retrieve(self, query: str, *, allowed_classifications: set[str] | None = None, limit: int = 5) -> list[dict]:
        allowed = allowed_classifications or {"PUBLIC", "INTERNAL"}
        terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
        results: list[tuple[int, RagSource, bool]] = []
        for src in self._sources.values():
            if src.revoked or src.classification not in allowed:
                continue
            score = sum(1 for t in terms if t in src.content.lower())
            if score <= 0:
                continue
            poison = any(marker in src.content.lower() for marker in INJECTION_MARKERS)
            results.append((score, src, poison))
        results.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "source_id": src.source_id,
                "content": src.content,
                "provenance": src.provenance,
                "classification": src.classification,
                "trust": src.trust,
                "source_hash": src.source_hash,
                "poison_suspected": poison,
                "score": score,
            }
            for score, src, poison in results[:limit]
        ]
