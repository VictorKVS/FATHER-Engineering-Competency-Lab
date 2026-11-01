from father_fua.local_models import DiscoveredModel
from father_fua.model_compatibility import evaluate_local_model


def test_compatible_local_model_passes():
    m=DiscoveredModel("OLLAMA","http://127.0.0.1:11434","m",True,True,True)
    r=evaluate_local_model(m,prompt_chars=1000)
    assert r.status=="PASS"
    assert r.reasons==()


def test_remote_or_unhealthy_model_denied():
    m=DiscoveredModel("OPENAI_COMPATIBLE","http://127.0.0.1:8000/v1","m",False,False,True)
    r=evaluate_local_model(m,prompt_chars=1000)
    assert r.status=="DENY"
    assert "model is not local" in r.reasons
    assert "model is not healthy" in r.reasons


def test_oversized_prompt_denied():
    m=DiscoveredModel("OLLAMA","http://127.0.0.1:11434","m",True,True,True)
    assert evaluate_local_model(m,prompt_chars=50000).status=="DENY"
