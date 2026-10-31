import unittest
from pathlib import Path

class EngineeringRolesUiTest(unittest.TestCase):
    def test_role_registry_contains_specialists(self):
        text=Path("factory/roles/ENGINEERING_ROLE_REGISTRY.yaml").read_text(encoding="utf-8")
        for token in (
            "AI Product Engineer",
            "Business Process Engineer",
            "System & Domain Engineer",
            "Security & Compliance Engineer",
            "Profession & Competency Engineer",
            "Corporate Knowledge Engineer",
            "Knowledge & Reasoning Engineer",
            "Research & Evidence Engineer",
        ):
            self.assertIn(token, text)

    def test_specialist_ui_exists(self):
        root=Path("factory/ui/father_site")
        for name in ("specialists.html","specialists.js","specialists.css","specialist.html","specialist.js","specialist.css"):
            self.assertTrue((root/name).exists(), name)

    def test_specialist_editor_has_professional_surfaces(self):
        html=Path("factory/ui/father_site/specialist.html").read_text(encoding="utf-8")
        for token in ("Input Package","Main Editor","Professional Logic","Metrics","A/B Testing","Handoff","Model Slot"):
            self.assertIn(token, html)

    def test_role_templates_exist(self):
        root=Path("factory/roles/templates")
        for name in (
            "PRODUCT_INTENT.yaml",
            "BUSINESS_PROCESS_MODEL.yaml",
            "SYSTEM_DOMAIN_MODEL.yaml",
            "SECURITY_ASSURANCE.yaml",
            "PROFESSION_COMPETENCY_MODEL.yaml",
            "CORPORATE_KNOWLEDGE_PACK.yaml",
            "RESEARCH_EXECUTION_PLAN.yaml",
        ):
            self.assertTrue((root/name).exists(), name)

    def test_agent_designer_links_roles(self):
        text=Path("factory/ui/father_site/index.html").read_text(encoding="utf-8")
        self.assertIn("./specialists.html", text)

if __name__=="__main__":
    unittest.main()
