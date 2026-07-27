"""CRUD de Livros."""
from typing import Optional
from sqlalchemy import or_
from src.core.database import DatabaseSession
from src.core.models import Book
from src.utils.logger import logger


class BooksCRUD:
    @staticmethod
    def create(n_tombo: str, isbn: str = "", editora: str = "", ano_edicao: str = "",
               classificacao: str = "", n_folhas: str = "", titulo: str = "",
               autor: str = "", volume: str = "", data_cadastro: str = "",
               assunto: str = "") -> Optional[Book]:
        try:
            with DatabaseSession() as session:
                book = Book(
                    n_tombo=n_tombo, isbn=isbn, editora=editora,
                    ano_edicao=ano_edicao, classificacao=classificacao,
                    n_folhas=n_folhas, titulo=titulo, autor=autor,
                    volume=volume, data_cadastro=data_cadastro, assunto=assunto,
                )
                session.add(book)
                logger.info("Book created: {} - {}", n_tombo, titulo)
                return book
        except Exception as e:
            logger.error("Error creating book: {}", e)
            return None

    @staticmethod
    def read_all() -> list[dict]:
        try:
            with DatabaseSession() as session:
                books = session.query(Book).order_by(Book.id.asc()).all()
                return [
                    {
                        "id": b.id, "n_tombo": b.n_tombo, "isbn": b.isbn,
                        "editora": b.editora, "ano_edicao": b.ano_edicao,
                        "classificacao": b.classificacao, "n_folhas": b.n_folhas,
                        "titulo": b.titulo, "autor": b.autor, "volume": b.volume,
                        "data_cadastro": b.data_cadastro, "assunto": b.assunto,
                    }
                    for b in books
                ]
        except Exception as e:
            logger.error("Error reading books: {}", e)
            return []

    @staticmethod
    def update(book_id: int, **kwargs) -> bool:
        try:
            with DatabaseSession() as session:
                book = session.query(Book).filter_by(id=book_id).first()
                if not book:
                    return False
                for key, value in kwargs.items():
                    if hasattr(book, key) and value is not None:
                        setattr(book, key, value)
                logger.info("Book updated: {}", book_id)
                return True
        except Exception as e:
            logger.error("Error updating book {}: {}", book_id, e)
            return False

    @staticmethod
    def delete(book_id: int) -> bool:
        try:
            with DatabaseSession() as session:
                book = session.query(Book).filter_by(id=book_id).first()
                if not book:
                    return False
                session.delete(book)
                logger.info("Book deleted: {}", book_id)
                return True
        except Exception as e:
            logger.error("Error deleting book {}: {}", book_id, e)
            return False

    @staticmethod
    def search(term: str) -> list[dict]:
        try:
            with DatabaseSession() as session:
                like = f"%{term}%"
                books = session.query(Book).filter(
                    or_(
                        Book.titulo.ilike(like), Book.autor.ilike(like),
                        Book.isbn.ilike(like), Book.n_tombo.ilike(like),
                        Book.classificacao.ilike(like), Book.editora.ilike(like),
                        Book.assunto.ilike(like),
                    )
                ).all()
                return [
                    {
                        "id": b.id, "n_tombo": b.n_tombo, "isbn": b.isbn,
                        "editora": b.editora, "ano_edicao": b.ano_edicao,
                        "classificacao": b.classificacao, "n_folhas": b.n_folhas,
                        "titulo": b.titulo, "autor": b.autor, "volume": b.volume,
                        "data_cadastro": b.data_cadastro, "assunto": b.assunto,
                    }
                    for b in books
                ]
        except Exception as e:
            logger.error("Error searching books: {}", e)
            return []

    @staticmethod
    def count() -> int:
        try:
            with DatabaseSession() as session:
                return session.query(Book).count()
        except Exception:
            return 0
