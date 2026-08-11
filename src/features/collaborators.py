"""CRUD de Colaboradores."""

from src.core.database import DatabaseSession
from src.core.models import Collaborator
from src.utils.crypto import hash_password, verify_password
from src.utils.logger import logger


class CollaboratorsCRUD:
    @staticmethod
    def create(nome: str, nome_usuario: str, senha: str,
               role: str = "collaborator") -> Collaborator | None:
        try:
            with DatabaseSession() as session:
                collab = Collaborator(
                    nome=nome,
                    nome_usuario=nome_usuario,
                    senha_hash=hash_password(senha),
                    role=role,
                )
                session.add(collab)
                logger.info("Collaborator created: {}", nome_usuario)
                return collab
        except Exception as e:
            logger.error("Error creating collaborator: {}", e)
            return None

    @staticmethod
    def authenticate(nome_usuario: str, senha: str) -> bool:
        try:
            with DatabaseSession() as session:
                collab = session.query(Collaborator).filter_by(
                    nome_usuario=nome_usuario
                ).first()
                if collab and verify_password(senha, collab.senha_hash):
                    logger.info("Collaborator authenticated: {}", nome_usuario)
                    return True
                logger.warning("Auth failed for: {}", nome_usuario)
                return False
        except Exception as e:
            logger.error("Error authenticating: {}", e)
            return False

    @staticmethod
    def read_all(safe: bool = True) -> list[dict]:
        """safe=True omite hashes de senha."""
        try:
            with DatabaseSession() as session:
                collabs = session.query(Collaborator).order_by(Collaborator.id.asc()).all()
                return [
                    {
                        "id": c.id, "nome": c.nome,
                        "nome_usuario": c.nome_usuario,
                        "senha": "********" if safe else c.senha_hash,
                        "role": c.role,
                    }
                    for c in collabs
                ]
        except Exception as e:
            logger.error("Error reading collaborators: {}", e)
            return []

    @staticmethod
    def update(collab_id: int, **kwargs) -> bool:
        try:
            with DatabaseSession() as session:
                collab = session.query(Collaborator).filter_by(id=collab_id).first()
                if not collab:
                    return False
                if "senha" in kwargs:
                    kwargs["senha_hash"] = hash_password(kwargs.pop("senha"))
                for key, value in kwargs.items():
                    if hasattr(collab, key) and value is not None:
                        setattr(collab, key, value)
                logger.info("Collaborator updated: {}", collab_id)
                return True
        except Exception as e:
            logger.error("Error updating collaborator {}: {}", collab_id, e)
            return False

    @staticmethod
    def delete(collab_id: int) -> bool:
        try:
            with DatabaseSession() as session:
                collab = session.query(Collaborator).filter_by(id=collab_id).first()
                if not collab:
                    return False
                session.delete(collab)
                logger.info("Collaborator deleted: {}", collab_id)
                return True
        except Exception as e:
            logger.error("Error deleting collaborator {}: {}", collab_id, e)
            return False

    @staticmethod
    def count() -> int:
        try:
            with DatabaseSession() as session:
                return session.query(Collaborator).count()
        except Exception:
            return 0

    @staticmethod
    def change_password(nome_usuario: str, new_password: str) -> bool:
        try:
            with DatabaseSession() as session:
                collab = session.query(Collaborator).filter_by(
                    nome_usuario=nome_usuario
                ).first()
                if not collab:
                    return False
                collab.senha_hash = hash_password(new_password)
                logger.info("Password changed for: {}", nome_usuario)
                return True
        except Exception as e:
            logger.error("Error changing password: {}", e)
            return False
