import unittest

from agents.alina.profiles.literary.automatic_eval import evaluate_story_record
from father_runtime.model_swap import ModelSwapRouter


def valid_record(model_id="M1", latency=100):
    return {
        "contract_valid": True,
        "latency_ms": latency,
        "input": {"target_length": 100},
        "output": {
            "continuation": " ".join(["слово"] * 80),
            "continuity": {
                "pov": "third",
                "tense": "past",
                "characters": ["Антон"],
                "open_threads_used": ["поезд"],
            },
            "canon_delta": [],
            "proposals": [],
            "model_id": model_id,
        },
    }


class StoryModelSwapTestCase(unittest.TestCase):
    def test_automatic_eval_passes_valid_contract(self):
        score, hard_fails = evaluate_story_record(valid_record())
        self.assertEqual(score, 100)
        self.assertEqual(hard_fails, [])

    def test_automatic_eval_rejects_missing_continuation(self):
        record = valid_record()
        record["output"]["continuation"] = ""
        score, hard_fails = evaluate_story_record(record)
        self.assertLess(score, 80)
        self.assertIn("continuation_empty", hard_fails)

    def test_router_switches_after_failure(self):
        router = ModelSwapRouter(pass_threshold=80)
        candidates = [{"id": "M1"}, {"id": "M2"}]

        def execute(candidate):
            if candidate["id"] == "M1":
                raise RuntimeError("model failed")
            return valid_record(model_id="M2", latency=200)

        selected, attempts = router.select(candidates, execute, evaluate_story_record)
        self.assertIsNotNone(selected)
        self.assertEqual(selected.model_id, "M2")
        self.assertEqual([x.status for x in attempts], ["RUNTIME_FAIL", "PASS"])

    def test_router_holds_when_no_model_passes(self):
        router = ModelSwapRouter(pass_threshold=80)
        selected, attempts = router.select(
            [{"id": "M1"}],
            lambda _: {"contract_valid": False, "output": {}, "input": {}},
            evaluate_story_record,
        )
        self.assertIsNone(selected)
        self.assertEqual(attempts[0].status, "FAIL")


if __name__ == "__main__":
    unittest.main()
