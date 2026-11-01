import time

from father_fua.human_acceptance import HumanAcceptance
from father_fua.installation_gate import evaluate_installation_gate
from father_fua.readiness import MANDATORY


def _all_auto_pass():
    return {name:"PASS" for name in MANDATORY if name!="HUMAN_ACCEPTANCE"}


def test_installation_gate_denies_without_human_acceptance():
    d=evaluate_installation_gate(
        current_snapshot_sha256="snap",
        acceptance=None,
        automated_gates=_all_auto_pass(),
    )
    assert d.decision=="DENIED"
    assert d.gates["HUMAN_ACCEPTANCE"]=="NOT_RUN"


def test_installation_gate_denies_wrong_snapshot_acceptance():
    a=HumanAcceptance(
        acceptance_id="HA-1",
        snapshot_sha256="old",
        requester="factory",
        approver="human",
        decision="ACCEPT",
        expires_at=time.time()+60,
    )
    d=evaluate_installation_gate(
        current_snapshot_sha256="new",
        acceptance=a,
        automated_gates=_all_auto_pass(),
    )
    assert d.decision=="DENIED"
    assert d.gates["HUMAN_ACCEPTANCE"]=="FAIL"


def test_installation_gate_denies_if_any_automated_gate_not_pass():
    a=HumanAcceptance(
        acceptance_id="HA-2",
        snapshot_sha256="snap",
        requester="factory",
        approver="human",
        decision="ACCEPT",
        expires_at=time.time()+60,
    )
    gates=_all_auto_pass()
    gates["SECURITY"]="FAIL"
    d=evaluate_installation_gate(
        current_snapshot_sha256="snap",
        acceptance=a,
        automated_gates=gates,
    )
    assert d.decision=="DENIED"


def test_installation_gate_passes_only_exact_snapshot_and_all_gates():
    a=HumanAcceptance(
        acceptance_id="HA-3",
        snapshot_sha256="snap",
        requester="factory",
        approver="human",
        decision="ACCEPT",
        expires_at=time.time()+60,
    )
    d=evaluate_installation_gate(
        current_snapshot_sha256="snap",
        acceptance=a,
        automated_gates=_all_auto_pass(),
    )
    assert d.decision=="PASS"
