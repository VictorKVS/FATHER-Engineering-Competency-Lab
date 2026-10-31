import unittest
from pathlib import Path

class GuidedFactoryDemoUiTest(unittest.TestCase):
    def test_demo_entry_exists(self):
        text=Path("factory/ui/father_site/index.html").read_text(encoding="utf-8")
        self.assertIn("./stage000.html?demo=story",text)

    def test_stage_000_hands_off_to_stage_001(self):
        text=Path("factory/ui/father_site/stage000.js").read_text(encoding="utf-8")
        self.assertIn('sessionStorage.setItem("nexus_stage_000"',text)
        self.assertIn("./stage001.html?demo=story",text)

    def test_stage_001_requires_stage_000_approval(self):
        text=Path("factory/ui/father_site/stage001.js").read_text(encoding="utf-8")
        self.assertIn('previous.human_gate.decision==="APPROVE"',text)
        self.assertIn("execution:{status:\"NOT_EXECUTED\"",text)

    def test_stage_001_shows_000_100_scaffold(self):
        text=Path("factory/ui/father_site/stage001.js").read_text(encoding="utf-8")
        self.assertIn("length:101",text)

if __name__=="__main__":
    unittest.main()
