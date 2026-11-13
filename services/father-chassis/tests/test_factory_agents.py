from father.engineering.factory_agents import build_factory_agent_catalog


def test_factory_agent_catalog_contains_separated_roles():
    catalog = build_factory_agent_catalog()
    ids = {agent.agent_id for agent in catalog.agents}

    assert {
        "FTH-AGENT-BUSINESS-ANALYST",
        "FTH-AGENT-SYSTEM-ANALYST",
        "FTH-AGENT-ALGORITHM-ENGINEER",
        "FTH-AGENT-ARCHITECT",
        "FTH-AGENT-TEST-ARCHITECT",
        "FTH-AGENT-SENIOR-DEVELOPER",
        "FTH-AGENT-DEVSECOPS",
        "FTH-AGENT-QUALIFICATION-AUDITOR",
    } <= ids


def test_each_agent_has_knowledge_contract_and_hash():
    catalog = build_factory_agent_catalog()

    for agent in catalog.agents:
        assert agent.contract_hash
        assert agent.knowledge_bases
        for kb in agent.knowledge_bases:
            assert kb.required_source_classes
            assert kb.required_entities
            assert kb.required_relationships


def test_developer_cannot_change_semantics_or_security():
    developer = build_factory_agent_catalog().by_id("FTH-AGENT-SENIOR-DEVELOPER")

    assert "change_approved_algorithm" in developer.forbidden_decisions
    assert "invent_api_field" in developer.forbidden_decisions
    assert "bypass_security_contract" in developer.forbidden_decisions


def test_qualification_auditor_cannot_invent_evidence():
    auditor = build_factory_agent_catalog().by_id("FTH-AGENT-QUALIFICATION-AUDITOR")

    assert "invent_evidence" in auditor.forbidden_decisions
    assert "block_qualification" in auditor.allowed_decisions
