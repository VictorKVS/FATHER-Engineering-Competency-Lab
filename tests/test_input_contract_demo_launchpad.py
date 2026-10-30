import unittest
from pathlib import Path

class InputContractDemoLaunchpadTest(unittest.TestCase):
    def test_three_demo_presets_are_in_input_modal(self):
        text=Path("factory/ui/father_site/app.js").read_text(encoding="utf-8")
        for token in (
            'data-demo-product="story"',
            'data-demo-product="osint"',
            'data-demo-product="security"',
            "Story / Model Swap",
            "OSINT Research",
            "Security Analysis",
        ):
            self.assertIn(token,text)

    def test_stage_000_supports_all_presets(self):
        text=Path("factory/ui/father_site/stage000.js").read_text(encoding="utf-8")
        self.assertIn("story:{",text)
        self.assertIn("osint:{",text)
        self.assertIn("security:{",text)

    def test_demo_launches_same_factory_entry(self):
        text=Path("factory/ui/father_site/app.js").read_text(encoding="utf-8")
        self.assertIn('location.href="./stage000.html?demo="+encodeURIComponent(demo)',text)

if __name__=="__main__":
    unittest.main()
