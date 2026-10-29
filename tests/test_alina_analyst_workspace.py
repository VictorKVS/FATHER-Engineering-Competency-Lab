import unittest
from pathlib import Path

class AlinaAnalystWorkspaceTest(unittest.TestCase):
    def test_alina_workspace_exists_and_supports_three_intelligence_blocks(self):
        root=Path("factory/ui/father_site")
        html=(root/"alina.html").read_text(encoding="utf-8")
        js=(root/"alina.js").read_text(encoding="utf-8")
        app=(root/"app.js").read_text(encoding="utf-8")
        self.assertIn("ALINA Analyst", html)
        for token in ("prompt","rag","kb"):
            self.assertIn(token, js)
        self.assertIn("Редактировать в ALINA", app)
        self.assertIn("alina.html?block=", app)

if __name__=="__main__":
    unittest.main()
