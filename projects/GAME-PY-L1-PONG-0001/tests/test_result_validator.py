import copy
import json
from pathlib import Path
import unittest

from factory.result_validator import validate_contract, validate_pair, validate_result


CONTRACT_PATH = Path(__file__).parents[1] / "experiments" / "EXP-RESULT-CONTRACT-0001.json"


def completed(arm):
    suffix = "A1" if arm == "baseline" else "B1"
    return {
        "schema_version": "0.1.0", "experiment_id": f"EXP-BREAKOUT-{suffix}", "arm": arm, "status": "completed",
        "runner": {"provider": "provider-x", "model": "model-y", "version": "2026-08", "context_instance_id": f"clean-{suffix}"},
        "budget": {"wall_clock_minutes": 45, "max_iterations": 3, "network_enabled": False, "token_input": 1000, "token_output": 2000},
        "preflight": {"inventory_sha256": "a" * 64, "contamination_check": "passed", "packet_sha256": ("b" if arm == "baseline" else "c") * 64},
        "timing": {"started_at": "2026-08-16T18:00:00+00:00", "first_test_run_at": "2026-08-16T18:10:00+00:00", "green_at": "2026-08-16T18:30:00+00:00", "time_to_green_minutes": 30},
        "metrics": {"first_pass_acceptance": 1, "critical_defects": 0, "defects_before_green": 1, "repeated_anti_patterns": 0, "architecture_deviations": 0, "security_findings": 0, "test_completeness": 0.9, "required_transition_coverage": 1.0, "non_test_source_lines": 300},
        "evidence": {"source_commit": "d" * 40, "test_command": "python -m unittest discover -s tests -v", "tests_passed": 8, "tests_total": 8, "compileall": "passed", "build_artifact": None, "review_ids": []},
        "learning_claim": "observation only", "parameter_training_performed": False, "decision": "accepted"
    }


class ResultValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_is_valid(self):
        validate_contract(self.contract)

    def test_complete_result_is_valid(self):
        self.assertEqual(validate_result(completed("baseline"), self.contract)["decision"], "result_valid")

    def test_missing_metric_is_rejected(self):
        result = completed("baseline"); result["metrics"]["test_completeness"] = None
        with self.assertRaisesRegex(ValueError, "missing metrics"):
            validate_result(result, self.contract)

    def test_accepted_result_requires_all_tests(self):
        result = completed("baseline"); result["evidence"]["tests_passed"] = 7
        with self.assertRaisesRegex(ValueError, "accepted result"):
            validate_result(result, self.contract)

    def test_parameter_training_claim_is_rejected(self):
        result = completed("baseline"); result["parameter_training_performed"] = True
        with self.assertRaisesRegex(ValueError, "parameter training"):
            validate_result(result, self.contract)

    def test_valid_pair_remains_single_observation(self):
        result = validate_pair(completed("baseline"), completed("treatment"), self.contract)
        self.assertEqual(result["decision"], "pair_valid_for_evaluation")
        self.assertEqual(result["role_promotion"], "not_evaluated")

    def test_model_mismatch_is_rejected(self):
        treatment = completed("treatment"); treatment["runner"]["model"] = "another-model"
        with self.assertRaisesRegex(ValueError, "runner mismatch"):
            validate_pair(completed("baseline"), treatment, self.contract)

    def test_reused_context_is_rejected(self):
        baseline, treatment = completed("baseline"), completed("treatment")
        treatment["runner"]["context_instance_id"] = baseline["runner"]["context_instance_id"]
        with self.assertRaisesRegex(ValueError, "distinct context"):
            validate_pair(baseline, treatment, self.contract)

    def test_budget_drift_is_rejected(self):
        treatment = completed("treatment"); treatment["budget"]["max_iterations"] = 4
        with self.assertRaisesRegex(ValueError, "budget mismatch"):
            validate_pair(completed("baseline"), treatment, self.contract)

    def test_input_fixture_is_not_mutated(self):
        baseline, treatment = completed("baseline"), completed("treatment")
        original = copy.deepcopy(baseline)
        validate_pair(baseline, treatment, self.contract)
        self.assertEqual(baseline, original)
