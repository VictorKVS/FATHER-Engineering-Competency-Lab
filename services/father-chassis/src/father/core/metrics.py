from __future__ import annotations

from collections import Counter
from time import perf_counter


class Metrics:
    def __init__(self) -> None:
        self.counters = Counter()
        self.timings_ms: list[float] = []

    def start(self) -> float:
        return perf_counter()

    def finish(self, started: float, success: bool) -> None:
        self.timings_ms.append((perf_counter() - started) * 1000)
        self.counters["requests_total"] += 1
        self.counters["requests_success" if success else "requests_failed"] += 1
