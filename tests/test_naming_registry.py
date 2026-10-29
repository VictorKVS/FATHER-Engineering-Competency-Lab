import unittest
from father_runtime.naming import NamingRegistry

class NamingRegistryTest(unittest.TestCase):
    def test_public_names_and_impact(self):
        r=NamingRegistry(".")
        self.assertEqual(r.public_name("SYS-001"),"NEXUS AI Systems Engineering")
        self.assertEqual(r.public_name("ROLE-001"),"Knowledge & Reasoning Engineer")
        impact=r.rename_impact("BLK-003","Instruction Engineering")
        self.assertEqual(impact["stable_id"],"BLK-003")
        self.assertIn("Prompt",impact["aliases_to_preserve"])
        self.assertTrue(impact["references_to_review"])

if __name__=="__main__":
    unittest.main()
