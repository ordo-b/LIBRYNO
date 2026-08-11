"""Validações de dados de entrada."""
import re

from src.utils.constants import MIN_NAME_LEN, MIN_PASSWORD_LEN, MIN_USERNAME_LEN


def validate_name(name: str) -> tuple[bool, str]:
    if not name or not name.strip():
        return False, "O nome não pode estar vazio."
    if len(name.strip()) < MIN_NAME_LEN:
        return False, f"O nome deve ter no mínimo {MIN_NAME_LEN} caracteres."
    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    if not username or not username.strip():
        return False, "O nome de usuário não pode estar vazio."
    if len(username.strip()) < MIN_USERNAME_LEN:
        return False, f"O usuário deve ter no mínimo {MIN_USERNAME_LEN} caracteres."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "A senha não pode estar vazia."
    if len(password) < MIN_PASSWORD_LEN:
        return False, f"A senha deve ter no mínimo {MIN_PASSWORD_LEN} caracteres."
    return True, ""


def validate_password_match(p1: str, p2: str) -> tuple[bool, str]:
    if p1 != p2:
        return False, "As senhas não conferem."
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    if not email:
        return True, ""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Email inválido."
    return True, ""


def validate_cpf(cpf: str) -> tuple[bool, str]:
    cpf_numbers = re.sub(r"\D", "", cpf)
    if len(cpf_numbers) != 11:
        return False, "CPF deve conter 11 dígitos."
    if cpf_numbers == cpf_numbers[0] * 11:
        return False, "CPF inválido."
    return True, ""


def validate_required_fields(fields: dict[str, str]) -> tuple[bool, str]:
    empty = [name for name, value in fields.items() if not value or not value.strip()]
    if empty:
        return False, f"Campos obrigatórios não preenchidos: {', '.join(empty)}"
    return True, ""


def validate_book(book_data: dict) -> tuple[bool, str]:
    required = {"Nº Tombo": book_data.get("n_tombo", ""), "Título": book_data.get("titulo", "")}
    ok, msg = validate_required_fields(required)
    if not ok:
        return False, msg
    return True, ""


def validate_reader(reader_data: dict) -> tuple[bool, str]:
    required = {
        "Nome": reader_data.get("nome", ""),
        "CPF": reader_data.get("cpf", ""),
        "Identidade": reader_data.get("identidade", ""),
    }
    ok, msg = validate_required_fields(required)
    if not ok:
        return False, msg
    ok, msg = validate_email(reader_data.get("email", ""))
    if not ok:
        return False, msg
    return True, ""
