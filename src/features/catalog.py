"""Catalogação avançada de livros (PREMIUM)."""
import json

from src.core.database import DatabaseSession
from src.core.models import Book
from src.utils.logger import logger


class CatalogCRUD:
    TAGS_PRESETS = [
        "Ficção", "Não-ficção", "Romance", "Técnico", "Didático",
        "Infantil", "Juvenil", "Referência", "Periódico", "Obra rara",
        "Arte", "Ciência", "História", "Filosofia", "Religião",
        "Direito", "Medicina", "Engenharia", "Educação", "Literatura",
    ]

    @staticmethod
    def set_tags(book_id: int, tags: list[str]) -> bool:
        try:
            with DatabaseSession() as session:
                book = session.query(Book).filter_by(id=book_id).first()
                if not book:
                    return False
                book.tags = json.dumps(tags, ensure_ascii=False)
                logger.info("Tags set for book {}: {}", book_id, tags)
                return True
        except Exception as e:
            logger.error("Error setting tags: {}", e)
            return False

    @staticmethod
    def get_tags(book_id: int) -> list[str]:
        try:
            with DatabaseSession() as session:
                book = session.query(Book).filter_by(id=book_id).first()
                if book and book.tags:
                    return json.loads(book.tags)
                return []
        except Exception:
            return []

    @staticmethod
    def set_synopsis(book_id: int, synopsis: str) -> bool:
        try:
            with DatabaseSession() as session:
                book = session.query(Book).filter_by(id=book_id).first()
                if not book:
                    return False
                book.synopsis = synopsis
                return True
        except Exception as e:
            logger.error("Error setting synopsis: {}", e)
            return False

    @staticmethod
    def set_cover(book_id: int, image_path: str) -> bool:
        try:
            with DatabaseSession() as session:
                book = session.query(Book).filter_by(id=book_id).first()
                if not book:
                    return False
                book.cover_image = image_path
                return True
        except Exception as e:
            logger.error("Error setting cover: {}", e)
            return False

    @staticmethod
    def search_by_tag(tag: str) -> list[dict]:
        try:
            with DatabaseSession() as session:
                books = session.query(Book).all()
                result = []
                for b in books:
                    if b.tags:
                        tags = json.loads(b.tags)
                        if tag in tags:
                            result.append({
                                "id": b.id, "titulo": b.titulo,
                                "autor": b.autor, "n_tombo": b.n_tombo,
                                "tags": tags,
                            })
                return result
        except Exception as e:
            logger.error("Error searching by tag: {}", e)
            return []

    @staticmethod
    def get_all_tags() -> dict[str, int]:
        try:
            tag_counts: dict[str, int] = {}
            with DatabaseSession() as session:
                books = session.query(Book).all()
                for b in books:
                    if b.tags:
                        for tag in json.loads(b.tags):
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            return dict(sorted(tag_counts.items(), key=lambda x: -x[1]))
        except Exception:
            return {}
