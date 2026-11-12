from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from typing import Any


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    source: str
    text: str
    chunk_id: str | int | None = None
    score: float | None = None
    locator: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("evidence source is required")
        if not self.text.strip():
            raise ValueError("evidence text is required")
        if not self.content_hash:
            object.__setattr__(self, "content_hash", sha256(self.text.encode("utf-8")).hexdigest())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_evidence(items: list[dict[str, Any] | EvidenceItem]) -> list[EvidenceItem]:
    result: list[EvidenceItem] = []
    for item in items:
        if isinstance(item, EvidenceItem):
            result.append(item)
            continue
        result.append(EvidenceItem(
            source=str(item.get("source", "unknown")),
            text=str(item.get("text", "")),
            chunk_id=item.get("chunk_id"),
            score=float(item["score"]) if item.get("score") is not None else None,
            locator=item.get("locator"),
            metadata=dict(item.get("metadata", {})),
            content_hash=str(item.get("content_hash", "")),
        ))
    return result
