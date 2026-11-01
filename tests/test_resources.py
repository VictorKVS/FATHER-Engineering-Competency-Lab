import pytest
from father_fua.resources import Budget


def test_budget_enforced():
    b = Budget(100,1.0)
    b.consume(tokens=50,money=0.5)
    with pytest.raises(RuntimeError):
        b.consume(tokens=60)



def test_budget_rejects_negative_consumption():
    b = Budget(100,1.0)
    with pytest.raises(ValueError):
        b.consume(tokens=-1)
    with pytest.raises(ValueError):
        b.consume(money=-0.01)
    assert b.tokens_used == 0
    assert b.money_used == 0.0


def test_budget_rejects_negative_limits():
    with pytest.raises(ValueError):
        Budget(-1,1.0)
    with pytest.raises(ValueError):
        Budget(1,-1.0)
