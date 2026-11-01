from __future__ import annotations
from dataclasses import dataclass


VALID_TRUST_LEVELS = {"TRUSTED", "UNTRUSTED", "UNKNOWN"}


@dataclass(frozen=True)
class ContextSegment:
    segment_id: str
    text: str
    priority: int
    mandatory: bool = False
    sensitive: bool = False
    source: str = "runtime"
    trust_level: str = "UNKNOWN"
    injection_suspected: bool = False


class ContextManager:
    def build(
        self,
        segments: list[ContextSegment],
        *,
        max_chars: int,
        remote_target: bool = False,
    ) -> list[ContextSegment]:
        if max_chars <= 0:
            raise ValueError("max_chars must be positive")

        for s in segments:
            if s.trust_level not in VALID_TRUST_LEVELS:
                raise ValueError("invalid context trust level")
            if s.injection_suspected and s.mandatory:
                raise ValueError("mandatory context cannot be injection-suspected")

        usable = [
            s
            for s in segments
            if not s.injection_suspected
            and not (remote_target and s.sensitive)
        ]

        mandatory = [s for s in usable if s.mandatory]
        optional = sorted(
            [s for s in usable if not s.mandatory],
            key=lambda s: (s.priority, s.trust_level == "TRUSTED"),
            reverse=True,
        )

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
