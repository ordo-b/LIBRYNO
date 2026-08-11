"""Testes unitários para validators."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.validators import (
    validate_book,
    validate_cpf,
    validate_email,
    validate_name,
    validate_password,
    validate_password_match,
    validate_reader,
    validate_required_fields,
    validate_username,
)


def test_validate_name():
    assert validate_name("Wesley") == (True, "")
    assert validate_name("We") == (False, "O nome deve ter no mínimo 3 caracteres.")
    assert validate_name("") == (False, "O nome não pode estar vazio.")


def test_validate_username():
    assert validate_username("admin") == (True, "")
    assert validate_username("ab") == (False, "O usuário deve ter no mínimo 3 caracteres.")


def test_validate_password():
    assert validate_password("12345") == (True, "")
    assert validate_password("1234") == (False, "A senha deve ter no mínimo 5 caracteres.")
    assert validate_password("") == (False, "A senha não pode estar vazia.")


def test_validate_password_match():
    assert validate_password_match("abc", "abc") == (True, "")
    assert validate_password_match("abc", "xyz") == (False, "As senhas não conferem.")


def test_validate_email():
    assert validate_email("test@email.com") == (True, "")
    assert validate_email("") == (True, "")  # optional
    assert validate_email("invalid") == (False, "Email inválido.")


def test_validate_cpf():
    assert validate_cpf("12345678901") == (True, "")
    assert validate_cpf("123") == (False, "CPF deve conter 11 dígitos.")


def test_validate_required_fields():
    ok, _ = validate_required_fields({"nome": "João", "email": "joao@email.com"})
    assert ok
    ok, _ = validate_required_fields({"nome": "", "email": "joao@email.com"})
    assert not ok


def test_validate_book():
    ok, _ = validate_book({"n_tombo": "001", "titulo": "Meu Livro"})
    assert ok
    ok, _ = validate_book({"n_tombo": "", "titulo": ""})
    assert not ok


def test_validate_reader():
    ok, _ = validate_reader({
        "nome": "João", "cpf": "12345678901", "identidade": "MG12345"
    })
    assert ok
    ok, _ = validate_reader({"nome": "", "cpf": "", "identidade": ""})
    assert not ok
