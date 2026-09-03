"""Testes unitários para BooksCRUD.

O BooksCRUD usa DatabaseSession() que depende do engine global.
Precisamos fazer patch do módulo database para apontar ao banco de testes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.core.models import Book


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


@pytest.fixture
def db_session(patch_database):
    Session = sessionmaker(bind=patch_database, expire_on_commit=False)
    s = Session()
    yield s
    s.close()


def test_create_book():
    from src.features.books import BooksCRUD
    book = BooksCRUD.create(
        n_tombo="001",
        titulo="O Pequeno Príncipe",
        autor="Antoine de Saint-Exupéry",
        isbn="978-85-7406-154-1",
    )
    assert book is not None
    assert book.n_tombo == "001"
    assert book.titulo == "O Pequeno Príncipe"


def test_read_all_books():
    from src.features.books import BooksCRUD
    BooksCRUD.create(n_tombo="001", titulo="Livro 1")
    BooksCRUD.create(n_tombo="002", titulo="Livro 2")
    books = BooksCRUD.read_all()
    assert len(books) == 2


def test_update_book():
    from src.features.books import BooksCRUD
    book = BooksCRUD.create(n_tombo="001", titulo="Título Original")
    ok = BooksCRUD.update(book.id, titulo="Título Atualizado")
    assert ok is True
    books = BooksCRUD.read_all()
    assert books[0]["titulo"] == "Título Atualizado"


def test_delete_book():
    from src.features.books import BooksCRUD
    book = BooksCRUD.create(n_tombo="001", titulo="Para Deletar")
    ok = BooksCRUD.delete(book.id)
    assert ok is True
    assert BooksCRUD.count() == 0


def test_search_books():
    from src.features.books import BooksCRUD
    BooksCRUD.create(n_tombo="001", titulo="Python para Iniciantes", autor="João")
    BooksCRUD.create(n_tombo="002", titulo="Java Avançado", autor="Maria")
    results = BooksCRUD.search("Python")
    assert len(results) == 1
    assert results[0]["titulo"] == "Python para Iniciantes"


def test_count_books():
    from src.features.books import BooksCRUD
    assert BooksCRUD.count() == 0
    BooksCRUD.create(n_tombo="001", titulo="Livro 1")
    BooksCRUD.create(n_tombo="002", titulo="Livro 2")
    assert BooksCRUD.count() == 2


def test_create_duplicate_tombo():
    from src.features.books import BooksCRUD
    BooksCRUD.create(n_tombo="001", titulo="Livro 1")
    result = BooksCRUD.create(n_tombo="001", titulo="Livro Duplicado")
    assert result is None  # unique constraint


def test_free_tier_limit():
    """Verifica que o FREE tier bloqueia criação acima do limite."""
    from src.features.books import BooksCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_BOOKS

    # Garantir que está em modo FREE
    was_premium = session.is_premium
    session._premium = False
    session._license_key = None

    # Criar livros até o limite
    for i in range(FREE_MAX_BOOKS):
        BooksCRUD.create(n_tombo=f"{i:04d}", titulo=f"Livro {i}")

    assert BooksCRUD.count() == FREE_MAX_BOOKS

    # Próximo deve falhar
    result = BooksCRUD.create(n_tombo="EXTRA", titulo="Não deve criar")
    assert result is None
    assert BooksCRUD.count() == FREE_MAX_BOOKS

    # Restaurar estado
    session._premium = was_premium


def test_premium_bypasses_limit():
    """Verifica que o tier PREMIUM não tem limite."""
    from src.features.books import BooksCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_BOOKS

    was_premium = session.is_premium
    session._premium = True
    session._license_key = "test-key"

    for i in range(FREE_MAX_BOOKS + 5):
        BooksCRUD.create(n_tombo=f"{i:04d}", titulo=f"Livro {i}")

    assert BooksCRUD.count() == FREE_MAX_BOOKS + 5

    session._premium = was_premium
