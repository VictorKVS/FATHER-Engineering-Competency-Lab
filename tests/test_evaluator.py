from father_fua.evaluator import CriterionResult, Evaluator


def test_all_evidenced_pass_is_pass():
    e = Evaluator()
    s = e.summarize([
        CriterionResult("C1", "PASS", "E1"),
        CriterionResult("C2", "PASS", "E2"),
    ])
    assert s.status == "PASS"


def test_missing_evidence_blocks():
    e = Evaluator()
    s = e.summarize([CriterionResult("C1", "PASS", None)])
    assert s.status == "BLOCKED"


def test_fail_overrides_pass():
    e = Evaluator()
    s = e.summarize([
        CriterionResult("C1", "PASS", "E1"),
        CriterionResult("SEC", "FAIL", "E2", "SECURITY"),
    ])
    assert s.status == "FAIL"
