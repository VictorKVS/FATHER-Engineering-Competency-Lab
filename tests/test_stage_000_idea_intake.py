import unittest
from tempfile import TemporaryDirectory

from father_runtime.idea_intake import GateDecision, IdeaIntakeEngine


class IdeaIntakeTest(unittest.TestCase):
    def test_input_test_blocks_empty_idea(self):
        with TemporaryDirectory() as d:
            engine=IdeaIntakeEngine(d)
            result=engine.input_test({"raw_idea": ""})
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("raw_idea_empty", result["failures"])

    def test_input_test_blocks_too_short_idea(self):
        with TemporaryDirectory() as d:
            engine=IdeaIntakeEngine(d)
            result=engine.input_test({"raw_idea": "коротко"})
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("raw_idea_too_short", result["failures"])

    def test_approved_stage_creates_only_project_proposal(self):
        with TemporaryDirectory() as d:
            engine=IdeaIntakeEngine(d)
            payload={"raw_idea": "Создать систему сменяемых LLM для продолжения рассказов с тестами."}
            analysis=engine.analyze(payload)
            record=engine.make_run(payload,analysis)
            approved=engine.apply_gate(record,GateDecision("APPROVE","human"))
            self.assertEqual(approved["state"],"APPROVED")
            self.assertEqual(approved["project_creation_proposal"]["mode"],"PROPOSAL_ONLY")
            self.assertEqual(approved["project_creation_proposal"]["github_repository"],"PENDING_APPROVAL")

    def test_hold_requires_reason(self):
        with TemporaryDirectory() as d:
            engine=IdeaIntakeEngine(d)
            payload={"raw_idea": "Создать систему сменяемых LLM для продолжения рассказов с тестами."}
            record=engine.make_run(payload,engine.analyze(payload))
            with self.assertRaises(ValueError):
                engine.apply_gate(record,GateDecision("HOLD","human"))

if __name__=="__main__":
    unittest.main()
