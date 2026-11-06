import unittest
from pathlib import Path


class FactoryEventTraceTest(unittest.TestCase):
    def test_primary_pages_load_trace_console(self):
        root=Path("factory/ui/father_site")
        pages=[
            "index.html","stage000.html","stage001.html","specialists.html",
            "specialist.html","traceability.html","alina.html","artifact.html","knowledge.html"
        ]
        for name in pages:
            text=(root/name).read_text(encoding="utf-8")
            self.assertIn("trace.js",text,name)
            self.assertIn("trace-console.js",text,name)
            self.assertIn("trace-console.css",text,name)

    def test_stage001_traces_state_transitions(self):
        text=Path("factory/ui/father_site/stage001.js").read_text(encoding="utf-8")
        for token in (
            'traceState("human_gate_approved"',
            'traceState("preflight_start"',
            'traceState("execution_start"',
            'traceState("verification_start"',
            'traceState("verification_result"',
        ):
            self.assertIn(token,text)

    def test_runtime_event_endpoint_exists(self):
        text=Path("father_runtime/site_runtime.py").read_text(encoding="utf-8")
        self.assertIn('if path == "/events":',text)
        self.assertIn("FactoryEventLogger",text)

    def test_event_log_is_append_only_jsonl(self):
        text=Path("father_runtime/event_log.py").read_text(encoding="utf-8")
        self.assertIn('with path.open("a"',text)
        self.assertIn(".jsonl",text)


if __name__=="__main__":
    unittest.main()
