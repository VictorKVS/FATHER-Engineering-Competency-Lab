from father_fua.planner import make_plan, validate_plan


def test_plan_has_dependencies_and_goal_links():
    p=make_plan("G1","mission")
    assert validate_plan(p)
    assert p[1].dependencies==("T1",)
