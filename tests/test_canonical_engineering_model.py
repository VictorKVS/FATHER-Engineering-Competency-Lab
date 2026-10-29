import unittest
from pathlib import Path
import yaml

from father_runtime.engineering_model import EngineeringModelValidator


class CanonicalEngineeringModelTest(unittest.TestCase):
    def test_core_files_exist(self):
        root=Path("factory/canonical")
        for name in ("CANONICAL_ENGINEERING_MODEL.yaml","TRACEABILITY_GRAPH.yaml","ENGINEERING_PROJECT.schema.yaml"):
            self.assertTrue((root/name).exists(), name)

    def test_minimal_project_validates(self):
        data=yaml.safe_load(Path("factory/canonical/examples/PROJECT_MINIMAL.yaml").read_text(encoding="utf-8"))
        result=EngineeringModelValidator().validate(data)
        self.assertTrue(result.valid, [i.code for i in result.issues])

    def test_missing_source_is_detected(self):
        data=yaml.safe_load(Path("factory/canonical/examples/PROJECT_MINIMAL.yaml").read_text(encoding="utf-8"))
        data["entities"]=[e for e in data["entities"] if e["id"]!="SRC-001"]
        data["edges"]=[e for e in data["edges"] if e["to"]!="SRC-001" and e["from"]!="SRC-001"]
        result=EngineeringModelValidator().validate(data)
        self.assertIn("KNOWLEDGE_NO_SOURCE",[i.code for i in result.issues])

    def test_traceability_ui_exists_and_is_linked(self):
        root=Path("factory/ui/father_site")
        for name in ("traceability.html","traceability.js","traceability.css"):
            self.assertTrue((root/name).exists(), name)
        index=(root/"index.html").read_text(encoding="utf-8")
        self.assertIn("./traceability.html",index)


if __name__=="__main__":
    unittest.main()
