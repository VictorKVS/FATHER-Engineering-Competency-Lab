from father_fua.identity import create_identity


def test_identity_instance_unique_and_hash_stable():
    a=create_identity(agent_id="A",version="1",owner="FATHER",trust_level="STANDARD")
    b=create_identity(agent_id="A",version="1",owner="FATHER",trust_level="STANDARD")
    assert a.instance_id != b.instance_id
    assert a.manifest_sha256 == b.manifest_sha256
