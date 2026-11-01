from father_fua.memory_runtime import MemoryItem, MemoryStore


def test_untrusted_low_confidence_memory_quarantined():
    m=MemoryStore()
    assert m.write(MemoryItem("claim","P","SRC",0.2))=="QUARANTINE"
    assert not m.items
