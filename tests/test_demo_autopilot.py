import json
import tempfile
import unittest
from pathlib import Path

import yaml

from father_runtime.demo_autopilot import DemoAutopilot


class DemoAutopilotTest(unittest.TestCase):
    def test_minimal_run_completes_all_101_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"stages").mkdir()
            (root/"project.yaml").write_text(
                yaml.safe_dump({
                    "project_id":"PRJ-TEST-001",
                    "state":"DRAFT",
                    "current_stage":"001",
                },sort_keys=False),
                encoding="utf-8",
            )
            for i in range(101):
                (root/"stages"/f"{i:03d}.yaml").write_text(
                    yaml.safe_dump({"stage_id":f"STAGE-{i:03d}"}),
                    encoding="utf-8",
                )

            result=DemoAutopilot().run(
                root=root,
                session_id="unit-test",
                project_id="PRJ-TEST-001",
                push=False,
            )

            self.assertEqual(result["status"],"HOLD")
            self.assertEqual(result["completed_stages"],101)
            self.assertTrue(result["final_checks"]["stage_files_101"])
            self.assertTrue(result["final_checks"]["artifacts_101"])
            self.assertTrue(result["final_checks"]["evidence_101"])
            self.assertTrue(result["final_checks"]["all_stages_approved"])
            self.assertTrue(result["final_checks"]["stage_100_approved"])
            self.assertTrue(result["final_checks"]["manifest_exists"])
            self.assertFalse(result["final_checks"]["git_commit_pass"])
            self.assertFalse(result["final_checks"]["git_push_pass"])

            project=yaml.safe_load((root/"project.yaml").read_text(encoding="utf-8"))
            self.assertEqual(project["state"],"DEMO_PRODUCTION_PROVEN")
            self.assertEqual(project["current_stage"],"100")

            for i in range(101):
                sid=f"{i:03d}"
                stage=yaml.safe_load((root/"stages"/f"{sid}.yaml").read_text(encoding="utf-8"))
                self.assertEqual(stage["state"],"APPROVED")
                self.assertEqual(stage["gate"],"DEMO_AUTO_APPROVED")
                self.assertEqual(stage["input_test"]["status"],"PASS")
                self.assertEqual(stage["artifact_test"]["status"],"PASS")
                self.assertTrue((root/"artifacts"/f"stage_{sid}"/"minimal_artifact.json").exists())
                evidence=root/"evidence"/f"stage_{sid}"/"demo_evidence.json"
                self.assertTrue(evidence.exists())
                payload=json.loads(evidence.read_text(encoding="utf-8"))
                self.assertEqual(payload["evidence_class"],"DEMO_ONLY")

    def test_home_links_autopilot_screen(self):
        text=Path("factory/ui/father_site/index.html").read_text(encoding="utf-8")
        self.assertIn("demo-autopilot.html",text)

    def test_runtime_exposes_autopilot_endpoint(self):
        text=Path("father_runtime/site_runtime.py").read_text(encoding="utf-8")
        self.assertIn('if path == "/demo/autopilot/run":',text)


if __name__=="__main__":
    unittest.main()
