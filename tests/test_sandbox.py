from father_fua.sandbox import SandboxPolicy, validate_path


def test_sandbox_defaults_to_no_network():
    assert SandboxPolicy().network_allowed is False


def test_path_requires_allowed_root():
    p = SandboxPolicy(allowed_roots=("G:/safe",))
    assert validate_path("G:/safe/file.txt",p) is True
    assert validate_path("C:/Windows/System32/x",p) is False
