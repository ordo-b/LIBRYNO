"""Testes de autenticação e enforcement OrdoB.

Valida que:
1. Sessão só é salva com assinatura HMAC
2. Sessão adulterada é descartada
3. Token validation é necessário no startup
4. FREE tier limits são respeitados
5. PREMIUM bypass funciona
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base


@pytest.fixture(autouse=True)
def patch_database(monkeypatch, tmp_path):
    """Substitui o engine global por um in-memory."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    import src.core.database as db_mod
    monkeypatch.setattr(db_mod, "_engine", engine)
    monkeypatch.setattr(db_mod, "_SessionLocal", TestSession)

    yield engine


@pytest.fixture
def clean_session(monkeypatch, tmp_path):
    """Cria sessão isolada para cada teste."""
    from src.auth.session import Session, SESSION_FILE
    test_session_file = tmp_path / ".session"
    monkeypatch.setattr("src.auth.session.SESSION_FILE", test_session_file)
    s = Session()
    return s


# ─── SESSION SECURITY ──────────────────────────────────────────

def test_session_save_load_roundtrip(clean_session):
    """Sessão salva e carregada deve preservar dados."""
    from src.auth.session import Session, SESSION_FILE

    clean_session.login("test-token-123", {"name": "Test", "email": "t@t.com"})
    clean_session.set_premium(True, "KEY-123")

    # Criar nova instância para forçar reload do arquivo
    loaded = Session()
    assert loaded.is_authenticated is True
    assert loaded.token == "test-token-123"
    assert loaded.is_premium is True
    assert loaded.license_key == "KEY-123"
    assert loaded.user_name == "Test"


def test_tampered_session_is_rejected(monkeypatch, tmp_path):
    """Sessão adulterada (HMAC inválido) deve ser descartada."""
    from src.auth.session import _sign, SESSION_FILE

    test_file = tmp_path / ".session"
    monkeypatch.setattr("src.auth.session.SESSION_FILE", test_file)

    data = {"token": "hacked", "user": {"name": "Hacker"}, "premium": True, "license_key": "STOLEN"}
    tampered = {"payload": data, "sig": "invalid-signature-here"}
    test_file.write_text(json.dumps(tampered), encoding="utf-8")

    from src.auth.session import Session
    loaded = Session()
    # Deve ter descartado a sessão
    assert loaded.is_authenticated is False
    assert loaded.is_premium is False


def test_valid_session_signature_accepted(monkeypatch, tmp_path):
    """Sessão com HMAC válido deve ser aceita."""
    from src.auth.session import _sign, SESSION_FILE

    test_file = tmp_path / ".session"
    monkeypatch.setattr("src.auth.session.SESSION_FILE", test_file)

    data = {"token": "valid-token", "user": {"name": "Valid"}, "premium": False, "license_key": ""}
    signed = {"payload": data, "sig": _sign(data)}
    test_file.write_text(json.dumps(signed), encoding="utf-8")

    from src.auth.session import Session
    loaded = Session()
    assert loaded.is_authenticated is True
    assert loaded.token == "valid-token"
    assert loaded.user_name == "Valid"


# ─── FREE TIER ENFORCEMENT ────────────────────────────────────

def test_free_tier_books_limit():
    """FREE tier não deve permitir mais de FREE_MAX_BOOKS livros."""
    from src.features.books import BooksCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_BOOKS

    was_premium = session.is_premium
    session._premium = False
    session._license_key = None

    for i in range(FREE_MAX_BOOKS):
        BooksCRUD.create(n_tombo=f"{i:04d}", titulo=f"Livro {i}")

    assert BooksCRUD.count() == FREE_MAX_BOOKS

    result = BooksCRUD.create(n_tombo="OVER", titulo="Bloqueado")
    assert result is None
    assert BooksCRUD.count() == FREE_MAX_BOOKS

    session._premium = was_premium


def test_free_tier_readers_limit():
    """FREE tier não deve permitir mais de FREE_MAX_READERS leitores."""
    from src.features.readers import ReadersCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_READERS

    was_premium = session.is_premium
    session._premium = False
    session._license_key = None

    for i in range(FREE_MAX_READERS):
        ReadersCRUD.create(nome=f"L{i}", cpf=f"{i:011d}")

    assert ReadersCRUD.count() == FREE_MAX_READERS

    result = ReadersCRUD.create(nome="Over", cpf="99999999999")
    assert result is None
    assert ReadersCRUD.count() == FREE_MAX_READERS

    session._premium = was_premium


def test_premium_unlimited_books():
    """PREMIUM não deve ter limite de livros."""
    from src.features.books import BooksCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_BOOKS

    was_premium = session.is_premium
    session._premium = True
    session._license_key = "PREMIUM-KEY"

    for i in range(FREE_MAX_BOOKS + 10):
        BooksCRUD.create(n_tombo=f"{i:04d}", titulo=f"Livro {i}")

    assert BooksCRUD.count() == FREE_MAX_BOOKS + 10

    session._premium = was_premium


def test_premium_unlimited_readers():
    """PREMIUM não deve ter limite de leitores."""
    from src.features.readers import ReadersCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_READERS

    was_premium = session.is_premium
    session._premium = True
    session._license_key = "PREMIUM-KEY"

    for i in range(FREE_MAX_READERS + 10):
        ReadersCRUD.create(nome=f"L{i}", cpf=f"{i:011d}")

    assert ReadersCRUD.count() == FREE_MAX_READERS + 10

    session._premium = was_premium


# ─── SESSION LOGOUT ────────────────────────────────────────────

def test_logout_clears_everything(clean_session):
    """Logout deve limpar todos os dados da sessão e o arquivo."""
    clean_session.login("token-xyz", {"name": "User", "email": "u@u.com"})
    clean_session.set_premium(True, "KEY")
    assert clean_session.is_authenticated is True

    clean_session.logout()
    assert clean_session.is_authenticated is False
    assert clean_session.token is None
    assert clean_session.is_premium is False
    assert clean_session.license_key is None


def test_login_sets_authenticated(clean_session):
    """Login deve marcar sessão como autenticada."""
    clean_session.login("tok", {"name": "N", "email": "e@e"})
    assert clean_session.is_authenticated is True
    assert clean_session.token == "tok"
    assert clean_session.user_name == "N"
