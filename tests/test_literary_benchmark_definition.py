import unittest
from pathlib import Path
import yaml


class LiteraryBenchmarkDefinitionTest(unittest.TestCase):
    def setUp(self):
        self.base=Path('agents/alina/profiles/literary/benchmark')

    def test_genre_suite_has_six_short_cases(self):
        doc=yaml.safe_load((self.base/'GENRE_SUITE.yaml').read_text(encoding='utf-8'))['suite']
        self.assertEqual(doc['max_target_words'],450)
        cases=doc['cases']
        self.assertEqual(len(cases),6)
        genres={x['genre'] for x in cases}
        self.assertEqual(genres,{'fantasy','thriller','romance','action','science_fiction','mystery'})

    def test_auto_matrix_has_four_enabled_text_models(self):
        doc=yaml.safe_load((self.base/'MODEL_MATRIX.yaml').read_text(encoding='utf-8'))['benchmark_models']
        enabled=[x for x in doc['candidates'] if x.get('enabled',True)]
        self.assertEqual(doc['automatic_local_candidates'],4)
        self.assertEqual(len(enabled),4)

    def test_rubric_has_provenance_labels(self):
        doc=yaml.safe_load((self.base/'EVALUATION_RUBRIC.yaml').read_text(encoding='utf-8'))['rubric']
        labels=doc['labels']
        for key in ('generator','agent','profile','prompt_version','rag_version','kb_version','evaluator_stage_1','evaluator_stage_2'):
            self.assertIn(key,labels)


if __name__=='__main__':
    unittest.main()
