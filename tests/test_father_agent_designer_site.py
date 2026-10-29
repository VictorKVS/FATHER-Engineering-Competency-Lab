import unittest
from pathlib import Path

class FatherAgentDesignerSiteTest(unittest.TestCase):
    def test_site_contains_canonical_agent_blocks(self):
        root=Path("factory/ui/father_site")
        html=(root/"index.html").read_text(encoding="utf-8")
        js=(root/"app.js").read_text(encoding="utf-8")
        self.assertIn("Agent Designer", html)
        self.assertIn("ALINA demo", html)
        for token in ("INPUT","ROLE","PROMPT","RAG","KB","MODEL_SLOT","OUTPUT","EVAL","EVIDENCE"):
            self.assertIn(token, js)

if __name__=="__main__":
    unittest.main()
