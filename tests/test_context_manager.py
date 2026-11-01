import pytest
from father_fua.context_manager import ContextManager, ContextSegment


def test_mandatory_retained_and_low_priority_dropped():
    cm = ContextManager()
    segs = [
        ContextSegment("policy","POLICY",100,mandatory=True),
        ContextSegment("high","AAAA",10),
        ContextSegment("low","BBBB",1),
    ]
    out = cm.build(segs,max_chars=10)
    assert [s.segment_id for s in out] == ["policy","high"]


def test_sensitive_removed_for_remote():
    cm = ContextManager()
    out = cm.build([
        ContextSegment("public","abc",1),
        ContextSegment("secret","xyz",2,sensitive=True),
    ],max_chars=100,remote_target=True)
    assert [s.segment_id for s in out] == ["public"]


def test_mandatory_overflow_fails():
    cm = ContextManager()
    with pytest.raises(ValueError):
        cm.build([ContextSegment("p","12345",1,mandatory=True)],max_chars=2)
