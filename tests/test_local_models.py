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
