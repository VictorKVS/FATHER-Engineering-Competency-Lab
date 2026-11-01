from father_fua.recovery import retry


def test_bounded_retry_recovers():
    n={"x":0}
    def op():
        n["x"] += 1
        if n["x"] < 3:
            raise RuntimeError("fail")
        return "ok"
    assert retry(op,attempts=3) == "ok"
