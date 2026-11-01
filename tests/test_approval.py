import time
from father_fua.approval import Approval, action_hash, verify_approval


def test_approval_bound_to_action_and_expiry():
    a = Approval(action_hash("tool.admin"),"human","APPROVE",time.time()+60)
    assert verify_approval(a,"tool.admin") is True
    assert verify_approval(a,"tool.other") is False
