import pytest
from linkedin_auto_applier.security import Security

def test_encrypt_decrypt_roundtrip():
    security = Security()
    original = {"foo": "bar", "num": 1}
    encrypted = security.encrypt_data(original)
    decrypted = security.decrypt_data(encrypted)
    assert decrypted == original
