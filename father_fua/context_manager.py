from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextSegment:
    segment_id: str
    text: str
    priority: int
    mandatory: bool = False
    sensitive: bool = False
    source: str = "runtime"


class ContextManager:
    def build(self, segments: list[ContextSegment], *, max_chars: int, remote_target: bool = False) -> list[ContextSegment]:
        usable = [s for s in segments if not (remote_target and s.sensitive)]
        mandatory = [s for s in usable if s.mandatory]
        optional = sorted([s for s in usable if not s.mandatory], key=lambda s: s.priority, reverse=True)
        out: list[ContextSegment] = []
        used = 0
        for s in mandatory + optional:
            size = len(s.text)
            if used + size <= max_chars:
                out.append(s)
                used += size
            elif s.mandatory:
                raise ValueError("mandatory context exceeds budget")
        return out
