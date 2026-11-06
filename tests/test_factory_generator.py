import tempfile
import unittest
from pathlib import Path

from father_runtime.generator import create_factory


class FactoryGeneratorTest(unittest.TestCase):
    def test_create_osint_factory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = create_factory('OSINT_FACTORY', repo_root='.', output_root=tmp)
            root = Path(result.output_dir)
            self.assertEqual(result.factory_id, 'FATHER-OSINT-FACTORY')
            self.assertTrue((root / 'factory_instance.yaml').exists())
            self.assertTrue((root / 'config' / 'factory_profile.yaml').exists())
            self.assertTrue((root / 'config' / 'agent_set.yaml').exists())
            self.assertTrue((root / 'README.md').exists())

    def test_unknown_profile_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                create_factory('NO_SUCH_FACTORY', repo_root='.', output_root=tmp)


if __name__ == '__main__':
    unittest.main()
