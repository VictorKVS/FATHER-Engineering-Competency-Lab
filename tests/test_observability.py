import pytest
from father_fua.observability import Metrics


def test_counter_and_latency():
    m = Metrics()
    m.inc("missions", labels={"agent":"A"})
    m.observe("latency", 0.12, labels={"agent":"A"})
    assert list(m.counters.values()) == [1]
    assert list(m.samples.values())[0] == [0.12]


def test_sensitive_label_rejected():
    m = Metrics()
    with pytest.raises(ValueError):
        m.inc("x", labels={"token":"abc"})
