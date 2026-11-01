from father_fua.recovery import retry


def test_bounded_retry_recovers():
    n={"x":0}
    def op():
        n["x"] += 1
        if n["x"] < 3:
            raise RuntimeError("fail")
        return "ok"
    assert retry(op,attempts=3) == "ok"



def test_retry_rejects_nonpositive_attempts():
    import pytest
    with pytest.raises(ValueError):
        retry(lambda: "ok", attempts=0)


def test_retry_does_not_repeat_permission_error():
    import pytest
    n={"x":0}
    def op():
        n["x"] += 1
        raise PermissionError("policy denied")
    with pytest.raises(PermissionError):
        retry(op, attempts=5)
    assert n["x"] == 1



def test_retry_does_not_repeat_validation_error():
    import pytest
    n={"x":0}
    def op():
        n["x"] += 1
        raise ValueError("invalid input")
    with pytest.raises(ValueError):
        retry(op, attempts=5)
    assert n["x"] == 1
