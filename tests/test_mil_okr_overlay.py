from pathlib import Path
import yaml


def test_military_overlay_covers_000_100_without_gaps():
    data=yaml.safe_load(
        Path("factory/project/MIL_OKR_DISCIPLINE_OVERLAY.yaml").read_text(encoding="utf-8")
    )["military_discipline_overlay"]
    covered=set()
    for gate in data["review_gates"]:
        raw=str(gate["stages"])
        if "-" in raw:
            start,end=(int(x) for x in raw.split("-",1))
        else:
            start=end=int(raw)
        covered.update(range(start,end+1))
    assert covered == set(range(101))


def test_every_review_gate_has_baseline_and_intent():
    data=yaml.safe_load(
        Path("factory/project/MIL_OKR_DISCIPLINE_OVERLAY.yaml").read_text(encoding="utf-8")
    )["military_discipline_overlay"]
    for gate in data["review_gates"]:
        assert gate["baseline"]
        assert gate["intent"]
