"""Migrações e setup do banco de dados."""
from src.core.database import init_database
from src.core.database import DatabaseSession
from src.core.models import Collaborator
from src.utils.crypto import hash_password
from src.utils.logger import logger


def setup_database():
    init_database()
    logger.info("Database initialized successfully")


def seed_admin():
    with DatabaseSession() as session:
        existing = session.query(Collaborator).filter_by(nome_usuario="admin").first()
        if not existing:
            admin = Collaborator(
                nome="Administrador",
                nome_usuario="admin",
                senha_hash=hash_password("admin123"),
                role="admin",
            )
            session.add(admin)
            logger.info("Default admin user created (admin/admin123)")
        else:
            logger.debug("Admin user already exists, skipping seed")
