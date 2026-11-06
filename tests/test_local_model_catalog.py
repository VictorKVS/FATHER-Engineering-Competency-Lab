import unittest
from pathlib import Path
import yaml

from agents.alina.profiles.literary.benchmark.runtime import LiteraryBenchmark


class LocalModelCatalogTest(unittest.TestCase):
    def test_catalog_counts_and_classes(self):
        doc=yaml.safe_load(Path('factory/model_fabric/LOCAL_MODEL_CATALOG.yaml').read_text(encoding='utf-8'))['catalog']
        self.assertEqual(doc['total_discovered_assets'],15)
        self.assertEqual(doc['one_agent_current_eligible_count'],7)
        self.assertEqual(len(doc['assets']),15)

    def test_one_agent_sweep_uses_catalog_eligibility(self):
        bench=LiteraryBenchmark(repo_root='.')
        models=bench.eligible_models()
        self.assertEqual(len(models),7)
        for model in models:
            self.assertIn(model['alina_literary'],{'ELIGIBLE','ELIGIBLE_EXPERIMENTAL'})
            self.assertIn(model['class'],{'TEXT_GENERATION','TEXT_CODE_GENERATION'})


if __name__=='__main__':
    unittest.main()
