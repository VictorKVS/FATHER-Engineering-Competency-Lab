import pytest

from father_fua.local_models import DiscoveredModel
from father_fua.real_model_runtime import RealModelMissionRuntime


MODEL=DiscoveredModel(
    transport="OLLAMA",
    base_url="http://127.0.0.1:11434",
    model_id="test-model",
    local=True,
    healthy=True,
    supports_chat=True,
)


def test_real_model_runtime_contract_with_fake_invoker():
    rt=RealModelMissionRuntime(
        discoverer=lambda:[MODEL],
        invoker=lambda model,prompt,timeout:"controlled model response",
    )
    r=rt.run("Describe FUA in one sentence.")
    assert r.model.model_id=="test-model"
    assert r.response=="controlled model response"
    assert len(r.response_sha256)==64
    assert len(r.evidence.sha256)==64
    assert r.audit_ok is True


def test_real_model_runtime_requires_local_model():
    remote=DiscoveredModel("OPENAI_COMPATIBLE","https://example.invalid/v1","remote",False,True,True)
    rt=RealModelMissionRuntime(discoverer=lambda:[remote])
    with pytest.raises(LookupError):
        rt.run("mission")


def test_real_model_runtime_policy_deny_blocks_call():
    called={"value":False}
    def invoker(model,prompt,timeout):
        called["value"]=True
        return "x"
    rt=RealModelMissionRuntime(discoverer=lambda:[MODEL],invoker=invoker)
    rt.policy.deny("FUA-001","model.call")
    with pytest.raises(PermissionError):
        rt.run("mission")
    assert called["value"] is False



def test_real_model_runtime_prefers_general_text_model():
    models=[
        DiscoveredModel("OLLAMA","http://127.0.0.1:11434","qwen3-vl:8b-instruct-q4_K_M",True,True,True),
        DiscoveredModel("OLLAMA","http://127.0.0.1:11434","qwen2.5:7b",True,True,True),
        DiscoveredModel("OLLAMA","http://127.0.0.1:11434","llava:7b",True,True,True),
    ]
    rt=RealModelMissionRuntime(discoverer=lambda:models)
    assert rt.choose_model().model_id=="qwen2.5:7b"



def test_real_model_runtime_retries_once_after_timeout():
    calls={"n":0}
    def invoker(model,prompt,timeout):
        calls["n"] += 1
        if calls["n"] == 1:
            raise TimeoutError("cold start")
        return "warmed response"
    rt=RealModelMissionRuntime(discoverer=lambda:[MODEL],invoker=invoker)
    r=rt.run("mission",timeout=1.0)
    assert r.response=="warmed response"
    assert calls["n"]==2
