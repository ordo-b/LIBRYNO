"""Testes unitários para crypto."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.crypto import hash_password, verify_password


def test_hash_password():
    hashed = hash_password("minha_senha")
    assert hashed != "minha_senha"
    assert len(hashed) > 0


def test_verify_password():
    hashed = hash_password("teste123")
    assert verify_password("teste123", hashed)
    assert not verify_password("errada", hashed)


def test_verify_wrong_type():
    assert not verify_password("test", "invalid_hash")
