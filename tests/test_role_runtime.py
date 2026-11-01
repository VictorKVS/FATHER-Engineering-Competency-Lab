from father_fua.role import Role, authorize_duty


def test_forbidden_overrides_allowed():
    r=Role("ANALYST",("search","admin"),("admin",),("LOCAL",))
    assert authorize_duty(r,"search") is True
    assert authorize_duty(r,"admin") is False
