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
