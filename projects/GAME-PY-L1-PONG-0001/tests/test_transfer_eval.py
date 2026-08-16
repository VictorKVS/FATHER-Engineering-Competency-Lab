import unittest

from factory.transfer_eval import evaluate_transfer


def pair(baseline, treatment):
    return {"baseline": baseline, "treatment": treatment}


BASE = {
    "critical_defects": 1,
    "time_to_green_minutes": 80,
    "architecture_deviations": 2,
    "first_pass_acceptance": 0,
    "test_completeness": 0.6,
}


class TransferEvaluationTests(unittest.TestCase):
    def test_requires_three_pairs_by_default(self):
        result = evaluate_transfer({"trials": [pair(BASE, BASE), pair(BASE, BASE)]})
        self.assertEqual(result["decision"], "insufficient_data")

    def test_promotes_only_a_candidate_when_two_metrics_improve(self):
        treatment = dict(BASE, critical_defects=0, time_to_green_minutes=60)
        result = evaluate_transfer({"trials": [pair(BASE, treatment)] * 3})
        self.assertEqual(result["decision"], "promote_candidate")
        self.assertIn("independent review", result["caveat"])

    def test_rejects_when_critical_defects_are_worse(self):
        treatment = dict(BASE, critical_defects=2, time_to_green_minutes=40, test_completeness=0.9)
        result = evaluate_transfer({"trials": [pair(BASE, treatment)] * 3})
        self.assertEqual(result["decision"], "reject")

    def test_rejects_non_numeric_metric(self):
        invalid = dict(BASE, test_completeness="high")
        with self.assertRaises(ValueError):
            evaluate_transfer({"trials": [pair(BASE, invalid)] * 3})
