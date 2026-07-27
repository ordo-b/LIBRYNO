"""Utilitários de criptografia e hash de senhas."""
import bcrypt


def hash_password(password: str) -> str:
    """Gera hash bcrypt de uma senha."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verifica se uma senha bate com o hash bcrypt."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
