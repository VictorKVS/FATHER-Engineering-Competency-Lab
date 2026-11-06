import unittest
from pathlib import Path


class TraceNumberingUiTest(unittest.TestCase):
    def test_runtime_has_daily_numbering(self):
        text=Path("father_runtime/event_log.py").read_text(encoding="utf-8")
        self.assertIn("next_daily_trace_number",text)
        self.assertIn('NEXUS_TRACE_{date_str}_{number:03d}.json',text)
        self.assertIn("reserve_trace_file",text)

    def test_runtime_has_trace_start_and_snapshot(self):
        text=Path("father_runtime/site_runtime.py").read_text(encoding="utf-8")
        self.assertIn('if path == "/trace/start":',text)
        self.assertIn('if path == "/trace/snapshot":',text)

    def test_ui_has_start_button_and_badge(self):
        text=Path("factory/ui/father_site/trace-console.js").read_text(encoding="utf-8")
        self.assertIn("НАЧАТЬ ТРАССИРОВКУ",text)
        self.assertIn("НОВАЯ ТРАССИРОВКА",text)
        self.assertIn("trace_number",text)
        self.assertIn("TRACE ",text)

    def test_trace_file_path_uses_desktop_factory_folder(self):
        text=Path("father_runtime/event_log.py").read_text(encoding="utf-8")
        self.assertIn('desktop / "Фабрика"',text)


if __name__=="__main__":
    unittest.main()
