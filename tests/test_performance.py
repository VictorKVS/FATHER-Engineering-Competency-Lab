import pytest
from father_fua.performance import PerformanceSample, meets_slo, summarize


def test_performance_summary_and_slo():
    samples=[
        PerformanceSample(10,True,100,0),
        PerformanceSample(20,True,100,0),
        PerformanceSample(30,True,100,0),
        PerformanceSample(40,True,100,0),
    ]
    s=summarize(samples)
    assert s.count==4
    assert s.success_rate==1.0
    assert s.p50_latency_ms==20
    assert s.p95_latency_ms==40
    assert s.tokens==400
    assert meets_slo(s,min_success_rate=.99,max_p95_latency_ms=100,max_cost=1.0)


def test_empty_samples_rejected():
    with pytest.raises(ValueError):
        summarize([])
