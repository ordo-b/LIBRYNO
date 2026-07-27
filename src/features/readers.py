"""CRUD de Leitores."""
from typing import Optional
from sqlalchemy import or_
from src.core.database import DatabaseSession
from src.core.models import Reader
from src.utils.logger import logger


class ReadersCRUD:
    @staticmethod
    def create(nome: str, telefone: str = "", email: str = "", cpf: str = "",
               identidade: str = "", cep: str = "", escolaridade: str = "",
               data_nascimento: str = "", endereco: str = "",
               data_cadastro: str = "") -> Optional[Reader]:
        try:
            with DatabaseSession() as session:
                reader = Reader(
                    nome=nome, telefone=telefone, email=email, cpf=cpf,
                    identidade=identidade, cep=cep, escolaridade=escolaridade,
                    data_nascimento=data_nascimento, endereco=endereco,
                    data_cadastro=data_cadastro,
                )
                session.add(reader)
                logger.info("Reader created: {} - CPF: {}", nome, cpf)
                return reader
        except Exception as e:
            logger.error("Error creating reader: {}", e)
            return None

    @staticmethod
    def read_all() -> list[dict]:
        try:
            with DatabaseSession() as session:
                readers = session.query(Reader).order_by(Reader.id.asc()).all()
                return [
                    {
                        "id": r.id, "nome": r.nome, "telefone": r.telefone,
                        "email": r.email, "cpf": r.cpf, "identidade": r.identidade,
                        "cep": r.cep, "escolaridade": r.escolaridade,
                        "data_nascimento": r.data_nascimento, "endereco": r.endereco,
                        "data_cadastro": r.data_cadastro,
                    }
                    for r in readers
                ]
        except Exception as e:
            logger.error("Error reading readers: {}", e)
            return []

    @staticmethod
    def update(reader_id: int, **kwargs) -> bool:
        try:
            with DatabaseSession() as session:
                reader = session.query(Reader).filter_by(id=reader_id).first()
                if not reader:
                    return False
                for key, value in kwargs.items():
                    if hasattr(reader, key) and value is not None:
                        setattr(reader, key, value)
                logger.info("Reader updated: {}", reader_id)
                return True
        except Exception as e:
            logger.error("Error updating reader {}: {}", reader_id, e)
            return False

    @staticmethod
    def delete(reader_id: int) -> bool:
        try:
            with DatabaseSession() as session:
                reader = session.query(Reader).filter_by(id=reader_id).first()
                if not reader:
                    return False
                session.delete(reader)
                logger.info("Reader deleted: {}", reader_id)
                return True
        except Exception as e:
            logger.error("Error deleting reader {}: {}", reader_id, e)
            return False

    @staticmethod
    def search(term: str) -> list[dict]:
        try:
            with DatabaseSession() as session:
                like = f"%{term}%"
                readers = session.query(Reader).filter(
                    or_(Reader.nome.ilike(like), Reader.cpf.ilike(like))
                ).all()
                return [
                    {
                        "id": r.id, "nome": r.nome, "telefone": r.telefone,
                        "email": r.email, "cpf": r.cpf, "identidade": r.identidade,
                        "cep": r.cep, "escolaridade": r.escolaridade,
                        "data_nascimento": r.data_nascimento, "endereco": r.endereco,
                        "data_cadastro": r.data_cadastro,
                    }
                    for r in readers
                ]
        except Exception as e:
            logger.error("Error searching readers: {}", e)
            return []

    @staticmethod
    def count() -> int:
        try:
            with DatabaseSession() as session:
                return session.query(Reader).count()
        except Exception:
            return 0
