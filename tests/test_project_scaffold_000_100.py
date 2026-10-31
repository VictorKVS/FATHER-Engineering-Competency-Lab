import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import yaml

from father_runtime.project_scaffold import ProjectScaffoldGenerator, STANDARD_DIRS


class ProjectScaffoldGeneratorTest(unittest.TestCase):
    def test_requires_explicit_approval(self):
        with TemporaryDirectory() as d:
            root=Path(d)/"project"
            with self.assertRaises(PermissionError):
                ProjectScaffoldGenerator().create(
                    root,
                    project_id="PRJ-T1",
                    public_name="Test",
                    code_name="TEST",
                    approved=False,
                )

    def test_creates_all_000_to_100_stage_files(self):
        with TemporaryDirectory() as d:
            root=Path(d)/"project"
            ProjectScaffoldGenerator().create(
                root,
                project_id="PRJ-T1",
                public_name="Test",
                code_name="TEST",
                approved=True,
            )
            files=sorted((root/"stages").glob("*.yaml"))
            self.assertEqual(len(files),101)
            self.assertEqual(files[0].name,"000.yaml")
            self.assertEqual(files[-1].name,"100.yaml")

            for rel in STANDARD_DIRS:
                self.assertTrue((root/rel).exists(), rel)

            s0=yaml.safe_load((root/"stages"/"000.yaml").read_text(encoding="utf-8"))
            s1=yaml.safe_load((root/"stages"/"001.yaml").read_text(encoding="utf-8"))
            s100=yaml.safe_load((root/"stages"/"100.yaml").read_text(encoding="utf-8"))
            self.assertEqual(s0["state"],"APPROVED")
            self.assertEqual(s1["state"],"READY")
            self.assertEqual(s100["stable_number"],"100")

    def test_stage_numbers_are_immutable_coordinate_system(self):
        stage_map=yaml.safe_load(Path("factory/project/PROJECT_STAGE_MAP.yaml").read_text(encoding="utf-8"))["project_stage_map"]
        self.assertTrue(stage_map["numbering"]["immutable"])
        self.assertEqual(stage_map["numbering"]["first"],0)
        self.assertEqual(stage_map["numbering"]["last"],100)


if __name__=="__main__":
    unittest.main()
