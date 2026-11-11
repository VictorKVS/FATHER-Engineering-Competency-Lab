from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_windows_qualification_scripts_exist():
    for name in ("check_env.ps1","start_local.ps1","smoke_test.ps1","recovery_test.ps1"):
        p = ROOT / "scripts" / name
        assert p.exists()
        assert p.stat().st_size > 100

def test_runbooks_are_bilingual():
    assert (ROOT/"docs"/"RUNBOOK_0_7_RU.md").exists()
    assert (ROOT/"docs"/"RUNBOOK_0_7_EN.md").exists()

def test_config_remains_windows_qualification_capable():
    cfg=json.loads((ROOT/"config"/"chassis.json").read_text(encoding="utf-8"))
    major, minor, patch = (int(x) for x in cfg["version"].split("."))
    assert (major, minor) >= (0, 7)
    assert cfg["metadata"]["profile"].startswith("windows-")
