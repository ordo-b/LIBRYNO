"""Testes de integração para banco de dados."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database import Base
from src.core.models import Book, Reader, Collaborator, Loan
from src.utils.crypto import hash_password


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_book(db_session):
    book = Book(n_tombo="001", titulo="Teste", autor="Autor", isbn="1234567890")
    db_session.add(book)
    db_session.commit()
    result = db_session.query(Book).first()
    assert result.titulo == "Teste"
    assert result.n_tombo == "001"


def test_create_reader(db_session):
    reader = Reader(nome="João", cpf="12345678901")
    db_session.add(reader)
    db_session.commit()
    result = db_session.query(Reader).first()
    assert result.nome == "João"


def test_create_collaborator(db_session):
    collab = Collaborator(
        nome="Admin", nome_usuario="admin",
        senha_hash=hash_password("12345"),
    )
    db_session.add(collab)
    db_session.commit()
    result = db_session.query(Collaborator).first()
    assert result.nome_usuario == "admin"


def test_create_loan(db_session):
    book = Book(n_tombo="002", titulo="Livro Emprestimo")
    reader = Reader(nome="Maria", cpf="98765432100")
    db_session.add_all([book, reader])
    db_session.commit()

    loan = Loan(
        book_id=book.id, reader_id=reader.id,
        data_emprestimo="2026-07-27",
        data_devolucao_prevista="2026-08-10",
    )
    db_session.add(loan)
    db_session.commit()
    result = db_session.query(Loan).first()
    assert result.status == "active"
    assert result.book.titulo == "Livro Emprestimo"
    assert result.reader.nome == "Maria"


def test_unique_constraint(db_session):
    book1 = Book(n_tombo="003", titulo="Livro A")
    db_session.add(book1)
    db_session.commit()

    book2 = Book(n_tombo="003", titulo="Livro B")
    db_session.add(book2)
    with pytest.raises(Exception):
        db_session.commit()
