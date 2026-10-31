import json
import tempfile
import unittest
from pathlib import Path

from father_runtime.adapters import ReferenceStage000Adapter
from father_runtime.runner import StageRunner


class FatherRuntimeTest(unittest.TestCase):
    def test_stage000_reference_run_is_reproducibly_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = StageRunner(repo_root=".", evidence_dir=tmp)
            record = runner.run(
                "factory/stages/STAGE_000_IDEA.yaml",
                "examples/father_stage000_input.yaml",
                ReferenceStage000Adapter(),
                "REFERENCE",
            )
            self.assertEqual(record["product_id"], "FATHER-PLATFORM")
            self.assertEqual(record["stage_id"], "000")
            self.assertEqual(record["result"]["status"], "PASS")
            self.assertTrue(record["metrics"]["schema_valid"])
            self.assertEqual(record["metrics"]["missing_required_fields"], [])
            self.assertTrue(Path(record["evidence_path"]).exists())

            saved = json.loads(Path(record["evidence_path"]).read_text(encoding="utf-8"))
            self.assertEqual(saved["result"]["status"], "PASS")
            self.assertIn("context_hash", saved["versions"])


if __name__ == "__main__":
    unittest.main()
