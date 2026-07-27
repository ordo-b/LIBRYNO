"""Sistema de notificações locais (PREMIUM)."""
from datetime import datetime
from typing import Optional
from src.core.database import DatabaseSession
from src.core.models import Notification
from src.utils.logger import logger


class NotificationsCRUD:
    @staticmethod
    def create(titulo: str, mensagem: str, tipo: str = "system") -> Optional[Notification]:
        try:
            with DatabaseSession() as session:
                notif = Notification(titulo=titulo, mensagem=mensagem, tipo=tipo)
                session.add(notif)
                logger.info("Notification created: {}", titulo)
                return notif
        except Exception as e:
            logger.error("Error creating notification: {}", e)
            return None

    @staticmethod
    def read_all(unread_only: bool = False) -> list[dict]:
        try:
            with DatabaseSession() as session:
                query = session.query(Notification)
                if unread_only:
                    query = query.filter_by(lida=False)
                notifs = query.order_by(Notification.created_at.desc()).all()
                return [
                    {
                        "id": n.id, "titulo": n.titulo, "mensagem": n.mensagem,
                        "tipo": n.tipo, "lida": n.lida,
                        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M") if n.created_at else "",
                    }
                    for n in notifs
                ]
        except Exception as e:
            logger.error("Error reading notifications: {}", e)
            return []

    @staticmethod
    def mark_read(notif_id: int) -> bool:
        try:
            with DatabaseSession() as session:
                n = session.query(Notification).filter_by(id=notif_id).first()
                if n:
                    n.lida = True
                    return True
                return False
        except Exception as e:
            logger.error("Error marking notification: {}", e)
            return False

    @staticmethod
    def mark_all_read() -> bool:
        try:
            with DatabaseSession() as session:
                session.query(Notification).filter_by(lida=False).update({Notification.lida: True})
                return True
        except Exception as e:
            logger.error("Error marking all notifications: {}", e)
            return False

    @staticmethod
    def delete(notif_id: int) -> bool:
        try:
            with DatabaseSession() as session:
                n = session.query(Notification).filter_by(id=notif_id).first()
                if n:
                    session.delete(n)
                    return True
                return False
        except Exception as e:
            logger.error("Error deleting notification: {}", e)
            return False

    @staticmethod
    def unread_count() -> int:
        try:
            with DatabaseSession() as session:
                return session.query(Notification).filter_by(lida=False).count()
        except Exception:
            return 0

    @staticmethod
    def notify_overdue_loans():
        from src.features.loans import LoansCRUD
        LoansCRUD.update_overdue()
        overdue = LoansCRUD.read_all(status="overdue")
        existing = NotificationsCRUD.read_all()
        existing_keys = set(n.get("mensagem", "") for n in existing)
        for loan in overdue:
            msg_key = f"overdue_{loan['id']}"
            if msg_key not in existing_keys:
                NotificationsCRUD.create(
                    titulo="Empréstimo em atraso",
                    mensagem=(
                        f"O livro '{loan['livro']}' está em atraso. "
                        f"Leitor: {loan['leitor']}. {msg_key}"
                    ),
                    tipo="loan_overdue",
                )
