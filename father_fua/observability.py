from __future__ import annotations
from collections import defaultdict


class Metrics:
    def __init__(self) -> None:
        self.counters: dict[tuple, int] = defaultdict(int)
        self.samples: dict[tuple, list[float]] = defaultdict(list)

    @staticmethod
    def _key(name: str, labels: dict[str, str] | None) -> tuple:
        labels = labels or {}
        forbidden = {"secret", "password", "token"}
        if any(k.lower() in forbidden for k in labels):
            raise ValueError("sensitive metric label")
        return (name, tuple(sorted(labels.items())))

    def inc(self, name: str, *, labels: dict[str, str] | None = None, value: int = 1) -> None:
        self.counters[self._key(name, labels)] += value

    def observe(self, name: str, value: float, *, labels: dict[str, str] | None = None) -> None:
        self.samples[self._key(name, labels)].append(value)
