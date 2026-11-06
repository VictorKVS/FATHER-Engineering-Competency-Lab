from father_fua.local_models import DiscoveredModel, invoke_model


def test_discovered_model_contract():
    m=DiscoveredModel("OLLAMA","http://127.0.0.1:11434","llama3.1",True,True,True)
    assert m.local is True
    assert m.healthy is True


def test_unsupported_transport_rejected():
    m=DiscoveredModel("X","http://127.0.0.1","m",True,True,True)
    try:
        invoke_model(m,"hello")
    except ValueError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("unsupported transport must be rejected")



def test_external_model_endpoint_rejected():
    from father_fua.local_models import _parse_loopback_http
    try:
        _parse_loopback_http("http://example.com:8000/v1")
    except ValueError as exc:
        assert "loopback" in str(exc)
    else:
        raise AssertionError("external endpoint must be rejected")


def test_file_scheme_rejected():
    from father_fua.local_models import _parse_loopback_http
    try:
        _parse_loopback_http("file:///etc/passwd")
    except ValueError:
        pass
    else:
        raise AssertionError("file scheme must be rejected")
