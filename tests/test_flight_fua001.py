from __future__ import annotations

from father_fua.evidence import verify_evidence
from father_fua.full_assembly import FullFUAAssemblyRuntime
from father_fua.local_models import DiscoveredModel
from father_fua.real_model_runtime import RealModelMissionRuntime


def test_maiden_flight_repeated_integrated_sorties():
    runtime=FullFUAAssemblyRuntime()
    missions=[
        "flight-01 nominal mission 01",
        "flight-01 nominal mission 02",
        "flight-01 knowledge read mission",
        "flight-01 policy boundary mission",
        "flight-01 tool boundary mission",
        "flight-01 audit mission",
        "flight-01 evidence mission",
        "flight-01 recovery readiness mission",
        "flight-01 compatibility mission",
        "flight-01 final nominal mission",
    ]
    results=[runtime.run(m) for m in missions]

    assert all(r.status=="PASS" for r in results)
    assert all(r.audit_ok is True for r in results)
    assert all(verify_evidence(r.evidence) for r in results)
    assert len({r.mission_id for r in results})==len(results)
    assert len({r.evidence.evidence_id for r in results})==len(results)
    assert runtime.audit.verify() is True
    assert all(r.answer["sandbox_network_allowed"] is False for r in results)
    assert all(r.answer["human_release_approved"] is False for r in results)
    assert all(r.answer["learning_proposal_approved"] is False for r in results)


def test_maiden_flight_real_model_contract_with_deterministic_invoker():
    model=DiscoveredModel(
        model_id="FLIGHT-TEST-LOCAL",
        transport="OLLAMA",
        base_url="http://127.0.0.1:11434",
        source="flight-test",
        local=True,
        healthy=True,
        supports_chat=True,
    )

    calls=[]

    def discoverer():
        return [model]

    def invoker(selected, prompt, timeout):
        calls.append((selected.model_id,prompt,timeout))
        return "FLIGHT_RESPONSE_OK"

    runtime=RealModelMissionRuntime(discoverer=discoverer,invoker=invoker)
    missions=[
        "flight model sortie one",
        "flight model sortie two",
        "flight model sortie three",
    ]
    results=[runtime.run(m,timeout=5.0) for m in missions]

    assert len(calls)==3
    assert all(r.model.model_id=="FLIGHT-TEST-LOCAL" for r in results)
    assert all(r.response=="FLIGHT_RESPONSE_OK" for r in results)
    assert all(r.audit_ok is True for r in results)
    assert all(verify_evidence(r.evidence) for r in results)
    assert runtime.audit.verify() is True
