from father_fua.governance_lifecycle import (
    ApiPolicy, LicenseRecord, NetworkPolicy, PrivacyRule, RecoveryPolicy,
    RetentionRule, StorageBinding, SupplyChainArtifact, deletion_allowed,
    validate_api_policy, validate_license, validate_network, validate_privacy,
    validate_recovery, validate_storage, validate_supply_chain,
)


def test_breaking_api_change_requires_notice():
    assert validate_api_policy(ApiPolicy("v2",True,True,True,0)) is False
    assert validate_api_policy(ApiPolicy("v2",True,True,True,30)) is True


def test_sensitive_storage_requires_encryption():
    assert validate_storage(StorageBinding("SECRET","vault",False)) is False
    assert validate_storage(StorageBinding("SECRET","vault",True)) is True


def test_network_is_deny_by_default():
    assert validate_network(NetworkPolicy("MODEL","ALLOW",())) is False
    assert validate_network(NetworkPolicy("MODEL","DENY",("127.0.0.1",))) is True


def test_recovery_requires_restore_test():
    assert validate_recovery(RecoveryPolicy(15,60,False)) is False
    assert validate_recovery(RecoveryPolicy(15,60,True)) is True


def test_supply_chain_requires_hash_sbom_signature_and_clean_scan():
    good=SupplyChainArtifact("fua","a"*64,True,True,"PASS")
    bad=SupplyChainArtifact("fua","a"*64,True,False,"PASS")
    assert validate_supply_chain(good) is True
    assert validate_supply_chain(bad) is False


def test_license_requires_use_permission():
    assert validate_license(LicenseRecord("x","MIT",True,True,False)) is True
    assert validate_license(LicenseRecord("x","X",False,False,False)) is False


def test_sensitive_privacy_rule_blocks_remote_model():
    assert validate_privacy(PrivacyRule("PII",True,30)) is False
    assert validate_privacy(PrivacyRule("PII",False,30)) is True


def test_legal_hold_blocks_deletion():
    assert deletion_allowed(RetentionRule("audit",30,True),365) is False
    assert deletion_allowed(RetentionRule("audit",30,False),31) is True
