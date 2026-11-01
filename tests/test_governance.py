from father_fua.governance import (
    AgentTrust, ChangeRequest, DataAssetPolicy, DeploymentProfile,
    can_delegate, validate_change, validate_data_policy, validate_deployment,
)
from father_fua.events import EventBus


def test_restricted_data_requires_encryption():
    p=DataAssetPolicy("Memory","RESTRICTED",30,False,True,("agent",),("agent",))
    assert validate_data_policy(p) is False


def test_air_gapped_profile_rejects_network_and_remote_models():
    bad=DeploymentProfile("AIR_GAPPED","EGRESS",True,"local-vault")
    good=DeploymentProfile("AIR_GAPPED","NONE",False,"local-vault")
    assert validate_deployment(bad) is False
    assert validate_deployment(good) is True


def test_sensitive_change_requires_recertification():
    assert validate_change(ChangeRequest("prompt","PROMPT",False)) is False
    assert validate_change(ChangeRequest("prompt","PROMPT",True)) is True


def test_agent_delegation_requires_auth_and_capability():
    a=AgentTrust("A",True,("delegate",),"L4")
    b=AgentTrust("B",True,("search",),"L3")
    assert can_delegate(a,b,"search") is True
    assert can_delegate(a,b,"admin") is False


def test_event_bus_idempotency_and_ordering():
    bus=EventBus()
    e1=bus.publish(correlation_id="C",kind="mission",payload={},idempotency_key="K1")
    e2=bus.publish(correlation_id="C",kind="mission",payload={},idempotency_key="K1")
    e3=bus.publish(correlation_id="C",kind="result",payload={},idempotency_key="K2")
    assert e1.event_id==e2.event_id
    assert e1.sequence==1
    assert e3.sequence==2
