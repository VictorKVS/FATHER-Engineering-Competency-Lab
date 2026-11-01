from father_fua.compatibility import CompatibilityMatrix


def test_unknown_combination_is_not_compatible():
    c = CompatibilityMatrix()
    assert c.is_approved("model","prompt") is False
    c.approve("model","prompt")
    assert c.is_approved("model","prompt") is True
