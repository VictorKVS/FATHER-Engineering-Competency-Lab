import unittest
from pathlib import Path
import yaml

class FactoryStageContractTest(unittest.TestCase):
    def test_stage_contract_requires_tests_evidence_and_human_gate(self):
        doc=yaml.safe_load(Path("factory/stages/STAGE_CONTRACT.yaml").read_text(encoding="utf-8"))["stage_contract"]
        self.assertEqual(
            doc["required_phases"],
            ["INPUT","INPUT_TEST","SPECIALIST_WORK","ARTIFACT_TEST","EVIDENCE","HUMAN_GATE"],
        )
        self.assertIn("automatic_analysis_cannot_self_approve",doc["invariant"])
        self.assertIn("next_stage_requires_approved_previous_stage",doc["invariant"])

    def test_stage_000_forbids_project_creation(self):
        doc=yaml.safe_load(Path("factory/stages/000_idea_intake/STAGE.yaml").read_text(encoding="utf-8"))["stage"]
        self.assertIn("do_not_create_github_repository",doc["prohibition"])
        self.assertIn("do_not_create_local_project",doc["prohibition"])
        self.assertTrue(doc["human_gate"]["required"])

    def test_stage_000_ui_is_factory_entry(self):
        root=Path("factory/ui/father_site")
        for name in ("stage000.html","stage000.css","stage000.js"):
            self.assertTrue((root/name).exists(),name)
        index=(root/"index.html").read_text(encoding="utf-8")
        self.assertIn("./stage000.html",index)

if __name__=="__main__":
    unittest.main()
