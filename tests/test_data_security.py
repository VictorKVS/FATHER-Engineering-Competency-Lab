import pytest
from father_fua.data_security import inspect_text, redact_secrets, remote_model_allowed


def test_normal_text_is_internal():
    r=inspect_text("FATHER architecture")
    assert r.classification=="INTERNAL"
    assert r.secret_like is False


@pytest.mark.parametrize("text",[
    "api_key=ABC123",
    "password: hunter2",
    "secret=xyz",
    "Authorization Bearer abc.def.ghi",
])
def test_credential_like_text_detected(text):
    r=inspect_text(text)
    assert r.secret_like is True
    assert r.classification=="CREDENTIAL"
    assert remote_model_allowed(text) is False


def test_redaction_removes_secret_value():
    out=redact_secrets("password=supersecret")
    assert "supersecret" not in out
    assert "[REDACTED]" in out


def test_oversized_input_rejected():
    with pytest.raises(ValueError):
        inspect_text("x"*1_000_001)
