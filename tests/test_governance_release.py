import pytest
from father_fua.governance_release import (
    AgentPackage, AutonomyPolicy, Capacity, DecommissionState, DomainPack,
    DOD_GATES, FinOpsBudget, IncidentState, SLO, decommission_complete,
    definition_of_done, incident_closed, validate_agent_package,
    validate_autonomy, validate_capacity, validate_domain_pack, validate_slo,
)


def test_domain_pack_requires_all_sections():
    p=DomainPack("ALINA",True,True,True,True,True,True,True,True,True)
    assert validate_domain_pack(p) is True


def test_agent_package_requires_signature_and_evidence():
    p=AgentPackage("A",True,True,True,True,True,True,True,True,True,False)
    assert validate_agent_package(p) is False


def test_slo_and_capacity_validation():
    assert validate_slo(SLO(.999,1000,.01,.99)) is True
    assert validate_capacity(Capacity(4,16,8,100,2,20)) is True


def test_finops_budget_enforced():
    b=FinOpsBudget(1.0)
    b.charge(.5)
    with pytest.raises(RuntimeError):
        b.charge(.6)


def test_runtime_autonomy_cannot_exceed_configured():
    assert validate_autonomy(AutonomyPolicy("L3","L2")) is True
    assert validate_autonomy(AutonomyPolicy("L2","L4")) is False


def test_incident_requires_recertification_to_close():
    s=IncidentState(True,True,True,True,False)
    assert incident_closed(s) is False


def test_decommission_requires_every_step():
    s=DecommissionState(True,True,True,True,True,True)
    assert decommission_complete(s) is True


def test_definition_of_done_denied_until_every_gate_passes():
    gates={k:"PASS" for k in DOD_GATES}
    gates["POLYGON"]="NOT_RUN"
    assert definition_of_done(gates)=="DENIED"
    gates["POLYGON"]="PASS"
    assert definition_of_done(gates)=="PRODUCTION_READY"
