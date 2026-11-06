import unittest

from father_runtime.agent_construct import AgentConstruct, AgentTournamentRunner


class AgentConstructTournamentTests(unittest.TestCase):
    def setUp(self):
        self.construct = AgentConstruct(
            agent_id="AG-STORY-001",
            purpose="Continue story",
            domain="STORY_CONTINUATION",
            role_version="ROLE-1",
            prompt_version="PROMPT-1",
            rag_version="RAG-1",
            knowledge_snapshot="KB-1",
            input_contract="IN-1",
            output_contract="OUT-1",
            eval_profile="EVAL-1",
            pass_threshold=80,
            hard_fail_rules=("contract_invalid", "canon_break"),
        )

    def test_only_model_changes_and_best_pass_wins(self):
        runner = AgentTournamentRunner(self.construct)
        scores = {"A": 82, "B": 91, "C": 99}

        def execute(candidate, context):
            return {
                "continuation": "ok",
                "model_id": candidate["id"],
                "frozen_prompt": context["agent"]["prompt_version"],
            }

        def evaluate(output, context):
            model = output["model_id"]
            hard = ["canon_break"] if model == "C" else []
            return scores[model], hard, {"quality": scores[model]}

        result = runner.run(
            task_input={"story_text": "Once"},
            candidates=[{"id": "A"}, {"id": "B"}, {"id": "C"}],
            execute=execute,
            evaluate=evaluate,
        )

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["winner"]["model_id"], "B")
        self.assertEqual(result["frozen_context"]["prompt_version"], "PROMPT-1")
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][2]["status"], "FAIL")

    def test_no_passing_model_returns_hold(self):
        runner = AgentTournamentRunner(self.construct)

        def execute(candidate, context):
            return {"model_id": candidate["id"]}

        def evaluate(output, context):
            return 70, [], {}

        result = runner.run(
            task_input={"x": 1},
            candidates=[{"id": "A"}, {"id": "B"}],
            execute=execute,
            evaluate=evaluate,
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertIsNone(result["winner"])


if __name__ == "__main__":
    unittest.main()
