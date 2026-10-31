import unittest

from agents.alina.profiles.literary.runtime import AlinaLiteraryRuntime


class AlinaLiteraryRuntimeTest(unittest.TestCase):
    def test_profile_loads_and_retrieves_knowledge(self):
        runtime = AlinaLiteraryRuntime(repo_root='.')
        chunks = runtime._retrieve('Антон вошел в теплицу и продолжил рассказ')
        self.assertTrue(chunks)
        self.assertTrue((runtime.profile_dir / 'PROMPT.md').exists())
        self.assertTrue((runtime.profile_dir / 'OUTPUT_CONTRACT.yaml').exists())


if __name__ == '__main__':
    unittest.main()
