from father_fua.policy import PolicyEngine


def test_default_deny():
    p = PolicyEngine()
    assert p.decide(subject="agent", action="tool.echo").decision == "DENY"


def test_explicit_allow():
    p = PolicyEngine()
    p.allow("agent", "tool.echo")
    assert p.decide(subject="agent", action="tool.echo").decision == "ALLOW"


def test_explicit_deny_overrides_allow():
    p = PolicyEngine()
    p.allow("agent", "tool.echo")
    p.deny("agent", "tool.echo")
    assert p.decide(subject="agent", action="tool.echo").decision == "DENY"


def test_restricted_data_blocks_remote_model():
    p = PolicyEngine()
    p.allow("agent", "model.call")
    d = p.decide(subject="agent", action="model.call", data_classification="RESTRICTED", target_model_location="REMOTE")
    assert d.decision == "DENY"


def test_privileged_action_requires_approval():
    p = PolicyEngine()
    p.allow("agent", "tool.admin")
    d = p.decide(subject="agent", action="tool.admin", privileged=True, human_approved=False)
    assert d.decision == "REQUIRE_APPROVAL"
