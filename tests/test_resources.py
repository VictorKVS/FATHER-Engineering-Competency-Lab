import pytest
from father_fua.resources import Budget


def test_budget_enforced():
    b = Budget(100,1.0)
    b.consume(tokens=50,money=0.5)
    with pytest.raises(RuntimeError):
        b.consume(tokens=60)
