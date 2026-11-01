from pathlib import Path

from father_fua.final_release_gate import evaluate_final_release


def test_current_repository_is_technically_eligible_but_not_released():
    decision=evaluate_final_release(Path("."))
    assert decision.allowed is True
    assert "final human release decision required" in decision.reason
