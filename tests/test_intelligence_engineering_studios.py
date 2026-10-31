import unittest
from pathlib import Path

class IntelligenceEngineeringStudiosTest(unittest.TestCase):
    def test_specialized_studios_exist(self):
        root=Path("factory/ui/father_site")
        for name in ("artifact.html","artifact.js","artifact.css","knowledge.html","knowledge.js","knowledge.css"):
            self.assertTrue((root/name).exists(), name)

    def test_agent_routes_intelligence_blocks(self):
        text=Path("factory/ui/father_site/app.js").read_text(encoding="utf-8")
        self.assertIn('artifact.html?artifact=role', text)
        self.assertIn('artifact.html?artifact=prompt', text)
        self.assertIn('artifact.html?artifact=rag', text)
        self.assertIn('./knowledge.html', text)

    def test_artifact_studio_has_required_engineering_surfaces(self):
        html=Path("factory/ui/father_site/artifact.html").read_text(encoding="utf-8")
        for token in ("Engineering Logic","Metrics","A/B Testing","Traceability","Evidence","Model Slot"):
            self.assertIn(token, html)

    def test_knowledge_architecture_has_layers_and_skill_formation(self):
        js=Path("factory/ui/father_site/knowledge.js").read_text(encoding="utf-8")
        for token in ("common_foundation","corporate_common","profession_core","specialist_domain","research_acquired","operational_dynamic","Competency Evidence"):
            self.assertIn(token, js)

    def test_reusable_knowledge_catalog_exists(self):
        text=Path("factory/knowledge/KNOWLEDGE_PACK_CATALOG.yaml").read_text(encoding="utf-8")
        for token in ("Professional Russian Language","Lawyer Core","Information Security Core","OSINT Core","DevOps / DevSecOps Core"):
            self.assertIn(token, text)

if __name__=="__main__":
    unittest.main()
