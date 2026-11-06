import pytest
from father_fua.skills import Skill, SkillRegistry


def test_skill_dependency_and_selection():
    r = SkillRegistry()
    r.register(Skill("base","1.0",("read",)))
    r.register(Skill("osint","1.0",("search",),("base",)))
    assert r.find("search")[0].skill_id == "osint"


def test_missing_dependency_rejected():
    r = SkillRegistry()
    with pytest.raises(ValueError):
        r.register(Skill("x","1.0",("a",),("missing",)))
