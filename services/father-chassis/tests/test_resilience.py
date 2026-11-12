

def test_call_with_retry_timeout_propagates_last_exception():
    from father.core.resilience import call_with_retry_timeout

    class BoomError(RuntimeError):
        pass

    def boom():
        raise BoomError("boom")

    try:
        call_with_retry_timeout(boom, attempts=2, timeout_ms=100)
    except BoomError as exc:
        assert str(exc) == "boom"
    else:
        raise AssertionError("BoomError was not propagated")
