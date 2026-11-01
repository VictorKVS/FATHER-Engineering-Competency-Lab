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


def test_budget_usage_can_reset_between_scopes():
    b=Budget(100,1.0)
    b.consume(tokens=80,money=0.75)
    assert b.tokens_used==80
    assert b.money_used==0.75

    b.reset_usage()

    assert b.tokens_used==0
    assert b.money_used==0.0
    b.consume(tokens=100,money=1.0)
    assert b.tokens_used==100
    assert b.money_used==1.0


def test_budget_reset_does_not_change_limits():
    b=Budget(10,0.5)
    b.consume(tokens=10,money=0.5)
    b.reset_usage()
    assert b.token_limit==10
    assert b.money_limit==0.5
    with pytest.raises(RuntimeError):
        b.consume(tokens=11)
