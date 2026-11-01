from father_fua.security_layer import security_gate


def test_open_high_security_finding_blocks():
    assert security_gate([{"severity":"HIGH","status":"OPEN"}]) == "DENY"
    assert security_gate([{"severity":"HIGH","status":"CLOSED"}]) == "ALLOW"
