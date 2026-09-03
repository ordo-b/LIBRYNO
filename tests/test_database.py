"""Testes de integração para banco de dados."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.core.models import Book, Collaborator, Loan, Reader
from src.utils.crypto import hash_password


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

    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_book(patch_database):
    book = Book(n_tombo="001", titulo="Teste", autor="Autor", isbn="1234567890")
    patch_database.add(book)
    patch_database.commit()
    result = patch_database.query(Book).first()
    assert result.titulo == "Teste"
    assert result.n_tombo == "001"


def test_create_reader(patch_database):
    reader = Reader(nome="João", cpf="12345678901")
    patch_database.add(reader)
    patch_database.commit()
    result = patch_database.query(Reader).first()
    assert result.nome == "João"


def test_create_collaborator(patch_database):
    collab = Collaborator(
        nome="Admin", nome_usuario="admin",
        senha_hash=hash_password("12345"),
    )
    patch_database.add(collab)
    patch_database.commit()
    result = patch_database.query(Collaborator).first()
    assert result.nome_usuario == "admin"


def test_create_loan(patch_database):
    book = Book(n_tombo="002", titulo="Livro Emprestimo")
    reader = Reader(nome="Maria", cpf="98765432100")
    patch_database.add_all([book, reader])
    patch_database.commit()

    loan = Loan(
        book_id=book.id, reader_id=reader.id,
        data_emprestimo="2026-07-27",
        data_devolucao_prevista="2026-08-10",
    )
    patch_database.add(loan)
    patch_database.commit()
    result = patch_database.query(Loan).first()
    assert result.status == "active"
    assert result.book.titulo == "Livro Emprestimo"
    assert result.reader.nome == "Maria"


def test_unique_constraint(patch_database):
    book1 = Book(n_tombo="003", titulo="Livro A")
    patch_database.add(book1)
    patch_database.commit()

    book2 = Book(n_tombo="003", titulo="Livro B")
    patch_database.add(book2)
    with pytest.raises(Exception):
        patch_database.commit()
