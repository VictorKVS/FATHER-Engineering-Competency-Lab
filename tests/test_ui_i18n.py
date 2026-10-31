import unittest
from pathlib import Path

class I18nUiTest(unittest.TestCase):
    def test_supported_languages(self):
        text=Path("factory/ui/father_site/i18n.js").read_text(encoding="utf-8")
        for token in ('["ru","Русский"]','["en","English"]','["de","Deutsch"]','["fr","Français"]','["es","Español"]','["zh-CN","中文"]'):
            self.assertIn(token,text)

    def test_language_persists(self):
        text=Path("factory/ui/father_site/i18n.js").read_text(encoding="utf-8")
        self.assertIn('localStorage.getItem(STORAGE_KEY)',text)
        self.assertIn('localStorage.setItem(STORAGE_KEY,lang)',text)

    def test_machine_identifiers_are_not_translated_by_runtime(self):
        text=Path("factory/ui/father_site/i18n.js").read_text(encoding="utf-8")
        self.assertIn('STAGE / ROLE / ID / YAML / JSON / пути не переводятся.',text)
        self.assertNotIn('"STAGE-001":',text)
        self.assertNotIn('"ROLE-101":',text)

    def test_i18n_connected_to_main_pages(self):
        root=Path("factory/ui/father_site")
        for name in ("index.html","stage000.html","stage001.html","specialists.html","specialist.html","traceability.html","alina.html","knowledge.html","artifact.html"):
            text=(root/name).read_text(encoding="utf-8")
            self.assertIn("./i18n.css",text,name)
            self.assertIn("./i18n.js",text,name)

    def test_dom_ids_remain_stable(self):
        index=Path("factory/ui/father_site/index.html").read_text(encoding="utf-8")
        self.assertIn('id="cloneAgent"',index)
        stage0=Path("factory/ui/father_site/stage000.html").read_text(encoding="utf-8")
        self.assertIn('id="stageState"',stage0)
        self.assertIn('id="approveStage"',stage0)
        stage1=Path("factory/ui/father_site/stage001.html").read_text(encoding="utf-8")
        self.assertIn('id="validateProposal"',stage1)
        self.assertIn('id="verificationState"',stage1)
        self.assertIn('id="approveGate"',stage1)

if __name__=="__main__":
    unittest.main()
