import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kb

class TestFrodoKB(unittest.TestCase):
    def test_integrity(self):
        stats = kb.validate()
        self.assertTrue(stats["valid"])
        self.assertGreater(stats["nodes"], 0)
    def test_known_rag(self):
        self.assertTrue(any("RAG" in n["title"].upper() for n in kb.search("RAG")))
    def test_prompt_injection(self):
        self.assertTrue(kb.search("prompt injection"))
    def test_missing(self):
        self.assertEqual(kb.search("NOT_A_REAL_KNOWLEDGE_TOPIC_987"), [])
    def test_no_execution(self):
        self.assertTrue(all(t["execution"] == "PLANNED" for t in kb.read("threat_catalog.json")))
    def test_authoritative_source(self):
        self.assertEqual(kb.read("source_manifest.json")["source_commit"], "2dc97586ab4286b3aff2032483c31c1d305904b5")

if __name__ == "__main__":
    unittest.main()
