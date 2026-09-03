"""Testes unitários para ReadersCRUD.

O ReadersCRUD usa DatabaseSession() que depende do engine global.
Precisamos fazer patch do módulo database para apontar ao banco de testes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base


@pytest.fixture(autouse=True)
def patch_database(monkeypatch):
    """Substitui o engine global por um in-memory para todos os testes."""
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


def test_create_reader():
    from src.features.readers import ReadersCRUD
    reader = ReadersCRUD.create(
        nome="João Silva",
        cpf="12345678901",
        email="joao@email.com",
        telefone="(22) 99999-9999",
    )
    assert reader is not None
    assert reader.nome == "João Silva"
    assert reader.cpf == "12345678901"


def test_read_all_readers():
    from src.features.readers import ReadersCRUD
    ReadersCRUD.create(nome="João", cpf="11111111111")
    ReadersCRUD.create(nome="Maria", cpf="22222222222")
    readers = ReadersCRUD.read_all()
    assert len(readers) == 2


def test_update_reader():
    from src.features.readers import ReadersCRUD
    reader = ReadersCRUD.create(nome="João", cpf="11111111111")
    ok = ReadersCRUD.update(reader.id, nome="João Atualizado")
    assert ok is True
    readers = ReadersCRUD.read_all()
    assert readers[0]["nome"] == "João Atualizado"


def test_delete_reader():
    from src.features.readers import ReadersCRUD
    reader = ReadersCRUD.create(nome="Para Deletar", cpf="11111111111")
    ok = ReadersCRUD.delete(reader.id)
    assert ok is True
    assert ReadersCRUD.count() == 0


def test_search_readers():
    from src.features.readers import ReadersCRUD
    ReadersCRUD.create(nome="João Silva", cpf="11111111111")
    ReadersCRUD.create(nome="Maria Santos", cpf="22222222222")
    results = ReadersCRUD.search("João")
    assert len(results) == 1
    assert results[0]["nome"] == "João Silva"


def test_count_readers():
    from src.features.readers import ReadersCRUD
    assert ReadersCRUD.count() == 0
    ReadersCRUD.create(nome="João", cpf="11111111111")
    assert ReadersCRUD.count() == 1


def test_create_duplicate_cpf():
    from src.features.readers import ReadersCRUD
    ReadersCRUD.create(nome="João", cpf="12345678901")
    result = ReadersCRUD.create(nome="Maria", cpf="12345678901")
    assert result is None  # unique constraint


def test_free_tier_limit():
    """Verifica que o FREE tier bloqueia criação acima do limite."""
    from src.features.readers import ReadersCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_READERS

    was_premium = session.is_premium
    session._premium = False
    session._license_key = None

    for i in range(FREE_MAX_READERS):
        ReadersCRUD.create(nome=f"Leitor {i}", cpf=f"{i:011d}")

    assert ReadersCRUD.count() == FREE_MAX_READERS

    result = ReadersCRUD.create(nome="Extra", cpf="99999999999")
    assert result is None
    assert ReadersCRUD.count() == FREE_MAX_READERS

    session._premium = was_premium


def test_premium_bypasses_limit():
    """Verifica que o tier PREMIUM não tem limite."""
    from src.features.readers import ReadersCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_READERS

    was_premium = session.is_premium
    session._premium = True
    session._license_key = "test-key"

    for i in range(FREE_MAX_READERS + 5):
        ReadersCRUD.create(nome=f"Leitor {i}", cpf=f"{i:011d}")

    assert ReadersCRUD.count() == FREE_MAX_READERS + 5

    session._premium = was_premium
