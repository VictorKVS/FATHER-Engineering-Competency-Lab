from dataclasses import replace
import pytest

from father_fua.backup_runtime import create_snapshot, restore_snapshot, verify_snapshot
from father_fua.incident_runtime import Incident, ORDER, advance, close_allowed


def test_snapshot_round_trip_and_integrity():
    payload={"state":{"status":"READY"},"memory":["x"],"version":"0.2"}
    s=create_snapshot("S1",payload)
    assert verify_snapshot(s) is True
    assert restore_snapshot(s)==payload


def test_snapshot_tamper_blocks_restore():
    s=create_snapshot("S1",{"x":1})
    bad=replace(s,payload_json='{"x":2}')
    assert verify_snapshot(bad) is False
    with pytest.raises(ValueError):
        restore_snapshot(bad)


def test_incident_requires_full_sequential_lifecycle():
    i=Incident("INC-1")
    for stage in ORDER[1:]:
        i=advance(i,stage)
    assert close_allowed(i) is True


def test_incident_cannot_skip_evidence_preservation():
    i=Incident("INC-1")
    with pytest.raises(ValueError):
        advance(i,"RECOVERED")
