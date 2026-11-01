import pytest
from father_fua.model_router import ModelProfile, ModelRouter


def test_router_prefers_compatible_lower_cost():
    r = ModelRouter()
    r.register(ModelProfile("local", "llama.cpp", "LOCAL", 8192, True, True, 0.1, "LOCAL_ONLY", True))
    r.register(ModelProfile("remote", "provider", "REMOTE", 128000, True, True, 2.0, "REMOTE_OK", True))
    assert r.select(require_tools=True).model_id == "local"


def test_local_only_blocks_remote():
    r = ModelRouter()
    r.register(ModelProfile("remote", "provider", "REMOTE", 128000, True, True, 0.1, "REMOTE_OK", True))
    with pytest.raises(LookupError):
        r.select(local_only=True)


def test_unhealthy_or_unapproved_model_not_selected():
    r = ModelRouter()
    r.register(ModelProfile("bad1", "x", "LOCAL", 8192, True, True, 0.1, "LOCAL_ONLY", False))
    r.register(ModelProfile("bad2", "x", "LOCAL", 8192, True, True, 0.1, "LOCAL_ONLY", True, approved=False))
    with pytest.raises(LookupError):
        r.select()


def test_context_and_cost_constraints_enforced():
    r = ModelRouter()
    r.register(ModelProfile("m1", "x", "LOCAL", 4096, True, True, 0.1, "LOCAL_ONLY", True))
    r.register(ModelProfile("m2", "x", "LOCAL", 32000, True, True, 5.0, "LOCAL_ONLY", True))
    with pytest.raises(LookupError):
        r.select(min_context=16000, max_cost=1.0)
