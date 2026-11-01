import pytest
from father_fua.learning import LearningGate, LearningProposal


def test_learning_requires_external_approval():
    g = LearningGate()
    p = LearningProposal("P1","GOLD_EXAMPLE","x","EVID-1")
    with pytest.raises(PermissionError):
        g.approve(p, external_approval=False)
    assert g.approve(p, external_approval=True).approved is True
