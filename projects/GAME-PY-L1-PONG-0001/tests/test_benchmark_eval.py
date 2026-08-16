import json
from pathlib import Path
import unittest

from factory.benchmark_eval import evaluate_attempt, validate_catalog


CATALOG_PATH = Path(__file__).parents[1] / "benchmarks" / "BENCHMARK-10-GAME-PROGRAMMER.json"


class BenchmarkEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    def attempt(self, score=0.9, evidence=None, critical=0):
        return {
            "task_id": "GAME-PY-L1-PONG-0001",
            "dimension_scores": {name: score for name in self.catalog["dimensions"]},
            "evidence": evidence or {},
            "critical_defects": critical,
        }

    def test_catalog_has_ten_ordered_tasks_and_normalized_weights(self):
        validate_catalog(self.catalog)

    def test_minimum_checkpoint_requires_named_evidence(self):
        evidence = {"requirements_pass": True, "core_tests_pass": True}
        result = evaluate_attempt(self.catalog, self.attempt(evidence=evidence))
        self.assertEqual(result["achieved_checkpoint"], "minimum")

    def test_standard_requires_cumulative_evidence(self):
        evidence = {key: True for key in (
            "requirements_pass", "core_tests_pass", "ci_matrix_pass", "package_self_check_pass"
        )}
        result = evaluate_attempt(self.catalog, self.attempt(evidence=evidence))
        self.assertEqual(result["achieved_checkpoint"], "standard")

    def test_critical_defect_blocks_all_checkpoints(self):
        evidence = {key: True for level in self.catalog["tasks"][0]["checkpoints"].values() for key in level}
        result = evaluate_attempt(self.catalog, self.attempt(evidence=evidence, critical=1))
        self.assertEqual(result["achieved_checkpoint"], "none")

    def test_result_never_claims_role_promotion(self):
        result = evaluate_attempt(self.catalog, self.attempt())
        self.assertEqual(result["role_promotion"], "not_evaluated")

    def test_scores_outside_unit_interval_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_attempt(self.catalog, self.attempt(score=1.1))
