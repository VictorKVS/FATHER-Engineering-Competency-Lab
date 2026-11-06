from father_fua.readiness import MANDATORY, release_decision


def test_release_denied_until_every_gate_passes():
    gates={k:"PASS" for k in MANDATORY}
    gates["SECURITY"]="NOT_RUN"
    assert release_decision(gates) == "DENIED"
    gates["SECURITY"]="PASS"
    assert release_decision(gates) == "PASS"
