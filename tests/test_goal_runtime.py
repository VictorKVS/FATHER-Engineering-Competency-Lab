import pytest
from father_fua.goal import create_goal


def test_goal_requires_measurable_bounds():
    g=create_goal("test",success=["done"],failure=["failed"],ttl_seconds=60)
    assert g.ttl_seconds==60
    with pytest.raises(ValueError):
        create_goal("x",success=[],failure=["f"])
