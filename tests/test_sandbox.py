from father_fua.sandbox import SandboxPolicy, validate_command, validate_output_size, validate_path


def test_sandbox_defaults_to_no_network():
    assert SandboxPolicy().network_allowed is False


def test_path_requires_allowed_root():
    p = SandboxPolicy(allowed_roots=("G:/safe",))
    assert validate_path("G:/safe/file.txt",p) is True
    assert validate_path("C:/Windows/System32/x",p) is False


def test_sibling_prefix_does_not_bypass_root():
    p=SandboxPolicy(allowed_roots=("G:/safe",))
    assert validate_path("G:/safeevil/file.txt",p) is False


def test_parent_traversal_cannot_escape_root():
    p=SandboxPolicy(allowed_roots=("G:/safe",))
    assert validate_path("G:/safe/../secret/file.txt",p) is False


def test_unc_and_device_paths_denied():
    p=SandboxPolicy(allowed_roots=("G:/safe",))
    assert validate_path(r"\\server\share\x",p) is False
    assert validate_path(r"\\?\C:\Windows\x",p) is False


def test_command_must_be_explicitly_allowlisted():
    p=SandboxPolicy(allowed_commands=("python.exe","git.exe"))
    assert validate_command("python.exe",p) is True
    assert validate_command(r"C:\Python\python.exe",p) is True
    assert validate_command("cmd.exe",p) is False


def test_output_size_is_bounded():
    p=SandboxPolicy(max_output_bytes=100)
    assert validate_output_size(100,p) is True
    assert validate_output_size(101,p) is False
