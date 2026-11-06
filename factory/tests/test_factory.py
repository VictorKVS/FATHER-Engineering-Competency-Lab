import json
import tempfile
import unittest
from pathlib import Path

from factory.runtime.factory import FactoryError, FACTORY_ROOT, assemble


class FactoryV01Tests(unittest.TestCase):
    def test_reference_product_assembles(self):
        product = FACTORY_ROOT / "products" / "hello_factory.json"
        manifest = assemble(product, write_evidence=False)
        self.assertEqual(manifest["assembly_status"], "PASS")
        self.assertEqual(manifest["chassis"]["id"], "C1_LIGHT_AGENT")
        self.assertEqual(len(manifest["blocks"]), 6)

    def test_missing_required_block_fails(self):
        source = json.loads(
            (FACTORY_ROOT / "products" / "hello_factory.json").read_text(encoding="utf-8")
        )
        source["blocks"].remove("FTH-BLOCK-GUARD-001")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaises(FactoryError):
                assemble(path, write_evidence=False)

    def test_unknown_block_fails(self):
        source = json.loads(
            (FACTORY_ROOT / "products" / "hello_factory.json").read_text(encoding="utf-8")
        )
        source["blocks"].append("FTH-BLOCK-UNKNOWN-999")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaises(FactoryError):
                assemble(path, write_evidence=False)


if __name__ == "__main__":
    unittest.main()
