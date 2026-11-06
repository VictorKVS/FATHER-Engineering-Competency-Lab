from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceSample:
    latency_ms: float
    success: bool
    tokens: int = 0
    cost: float = 0.0


@dataclass(frozen=True)
class PerformanceSummary:
    count: int
    success_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    tokens: int
    cost: float


def _percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("no values")
    vals=sorted(values)
    idx=max(0,min(len(vals)-1,math.ceil(q*len(vals))-1))
    return vals[idx]


def summarize(samples: list[PerformanceSample]) -> PerformanceSummary:
    if not samples:
        raise ValueError("no samples")
    latencies=[s.latency_ms for s in samples]
    return PerformanceSummary(
        count=len(samples),
        success_rate=sum(1 for s in samples if s.success)/len(samples),
        p50_latency_ms=_percentile(latencies,.50),
        p95_latency_ms=_percentile(latencies,.95),
        tokens=sum(s.tokens for s in samples),
        cost=sum(s.cost for s in samples),
    )


def meets_slo(
    summary: PerformanceSummary,
    *,
    min_success_rate: float,
    max_p95_latency_ms: float,
    max_cost: float,
) -> bool:
    return (
        summary.success_rate >= min_success_rate
        and summary.p95_latency_ms <= max_p95_latency_ms
        and summary.cost <= max_cost
    )
