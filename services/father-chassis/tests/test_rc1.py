from pathlib import Path
from father.rc.qualification import run_checks
from father.rc.compatibility import check_chassis_compatibility
from father.rc.fallback import FailingModel, FallbackModel
from father.core.model_router import ModelRouter

ROOT = Path(__file__).resolve().parents[1]

def test_rc_report_passes_when_all_checks_pass():
    r = run_checks([
        ("a", lambda: {"passed": True, "value": 1}),
        ("b", lambda: {"passed": True, "value": 2}),
    ])
    assert r.passed
    assert len(r.checks) == 2

def test_rc_report_fails_closed():
    r = run_checks([
        ("good", lambda: {"passed": True}),
        ("bad", lambda: (_ for _ in ()).throw(RuntimeError("boom"))),
    ])
    assert not r.passed
    assert r.checks[1].passed is False

def test_incompatible_block_rejected():
    ok = check_chassis_compatibility("father-chassis>=0.4,<2.0", "1.0.0rc1")
    bad = check_chassis_compatibility("other-platform>=1", "1.0.0rc1")
    assert ok.compatible
    assert not bad.compatible

def test_model_fallback_router():
    primary = FailingModel()
    fallback = FallbackModel()
    router = ModelRouter(
        {primary.name: primary, fallback.name: fallback},
        default=primary.name,
        fallbacks=(fallback.name,),
    )
    selected = router.resolve()
    assert selected.name == "healthy-fallback"
    assert selected.generate("hello", []) == "fallback:hello"

def test_rc_scripts_exist():
    for name in ("factory_rc_test.ps1", "build_rc_report.ps1"):
        p = ROOT/"scripts"/name
        assert p.exists()
        assert p.stat().st_size > 200
