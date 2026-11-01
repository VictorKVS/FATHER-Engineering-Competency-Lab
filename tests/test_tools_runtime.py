import pytest
from father_fua.tools_runtime import ToolRuntime, ToolSpec


def test_allowed_tool_executes_and_audits():
    rt = ToolRuntime()
    rt.register(ToolSpec("echo", False, ("ANALYST",)), lambda p: {"echo": p["x"]})
    result = rt.execute("echo", {"x": 1}, role="ANALYST", policy_allow=True)
    assert result == {"echo": 1}
    assert rt.audit[-1]["status"] == "EXECUTED"


def test_unknown_tool_denied():
    rt = ToolRuntime()
    with pytest.raises(PermissionError):
        rt.execute("missing", {}, role="ANALYST", policy_allow=True)


def test_policy_denial_blocks_execution():
    rt = ToolRuntime()
    rt.register(ToolSpec("echo", False, ("ANALYST",)), lambda p: p)
    with pytest.raises(PermissionError):
        rt.execute("echo", {}, role="ANALYST", policy_allow=False)


def test_privileged_tool_requires_human_approval():
    rt = ToolRuntime()
    rt.register(ToolSpec("danger", True, ("ADMIN",)), lambda p: p)
    with pytest.raises(PermissionError):
        rt.execute("danger", {}, role="ADMIN", policy_allow=True, human_approved=False)
    assert rt.execute("danger", {"ok": True}, role="ADMIN", policy_allow=True, human_approved=True)["ok"] is True



def test_tool_rate_limit_enforced():
    rt=ToolRuntime()
    rt.register(ToolSpec("limited",False,("ANALYST",),max_calls=1),lambda p:p)
    assert rt.execute("limited",{"x":1},role="ANALYST",policy_allow=True)=={"x":1}
    with pytest.raises(RuntimeError):
        rt.execute("limited",{"x":2},role="ANALYST",policy_allow=True)
    assert rt.calls_used("limited")==1
    assert rt.audit[-1]["status"]=="RATE_LIMITED"



def test_tool_runtime_audits_denials_and_handler_failures():
    rt=ToolRuntime()

    def failing_handler(payload):
        raise RuntimeError("handler failure")

    rt.register(
        ToolSpec("admin",True,("ANALYST",),max_calls=2),
        failing_handler,
    )

    with pytest.raises(PermissionError):
        rt.execute("missing",{},role="ANALYST",policy_allow=True)
    assert rt.audit[-1]["status"]=="DENIED"
    assert rt.audit[-1]["reason"]=="UNKNOWN_TOOL"

    with pytest.raises(PermissionError):
        rt.execute("admin",{},role="ANALYST",policy_allow=False)
    assert rt.audit[-1]["status"]=="DENIED"
    assert rt.audit[-1]["reason"]=="POLICY"

    with pytest.raises(PermissionError):
        rt.execute("admin",{},role="ANALYST",policy_allow=True,human_approved=False)
    assert rt.audit[-1]["reason"]=="HUMAN_APPROVAL"

    with pytest.raises(RuntimeError):
        rt.execute("admin",{},role="ANALYST",policy_allow=True,human_approved=True)
    assert rt.audit[-1]["status"]=="FAILED"
    assert rt.audit[-1]["error_type"]=="RuntimeError"
    assert rt.calls_used("admin")==0


def test_tool_runtime_rejects_invalid_registration():
    rt=ToolRuntime()
    with pytest.raises(ValueError):
        rt.register(ToolSpec("",False,("ANALYST",)),lambda p:p)
    with pytest.raises(ValueError):
        rt.register(ToolSpec("x",False,()),lambda p:p)


def test_tool_call_budget_can_reset_between_scopes_without_losing_audit():
    rt=ToolRuntime()
    rt.register(ToolSpec("limited",False,("ANALYST",),max_calls=1),lambda p:p)

    assert rt.execute("limited",{"x":1},role="ANALYST",policy_allow=True)=={"x":1}
    assert rt.calls_used("limited")==1
    audit_len=len(rt.audit)

    rt.reset_call_budget("limited")
    assert rt.calls_used("limited")==0
    assert len(rt.audit)==audit_len
    assert rt.execute("limited",{"x":2},role="ANALYST",policy_allow=True)=={"x":2}


def test_tool_call_budget_reset_rejects_unknown_tool():
    rt=ToolRuntime()
    with pytest.raises(KeyError):
        rt.reset_call_budget("missing")
