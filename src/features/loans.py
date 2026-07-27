"""Sistema de empréstimos de livros (PREMIUM)."""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import or_
from src.core.database import DatabaseSession
from src.core.models import Loan, Book, Reader
from src.utils.constants import DEFAULT_LOAN_DAYS, FINE_PER_DAY, LOAN_STATUS_ACTIVE, LOAN_STATUS_RETURNED, LOAN_STATUS_OVERDUE
from src.utils.logger import logger


class LoansCRUD:
    @staticmethod
    def create(book_id: int, reader_id: int, days: int = DEFAULT_LOAN_DAYS,
               notes: str = "") -> Optional[Loan]:
        try:
            with DatabaseSession() as session:
                book = session.query(Book).filter_by(id=book_id).first()
                reader = session.query(Reader).filter_by(id=reader_id).first()
                if not book or not reader:
                    return None

                active = session.query(Loan).filter_by(
                    book_id=book_id, status=LOAN_STATUS_ACTIVE
                ).first()
                if active:
                    logger.warning("Book {} already on loan", book_id)
                    return None

                now = datetime.now()
                loan = Loan(
                    book_id=book_id,
                    reader_id=reader_id,
                    data_emprestimo=now.strftime("%Y-%m-%d"),
                    data_devolucao_prevista=(now + timedelta(days=days)).strftime("%Y-%m-%d"),
                    status=LOAN_STATUS_ACTIVE,
                    observacoes=notes,
                )
                session.add(loan)
                logger.info("Loan created: book={} reader={}", book_id, reader_id)
                return loan
        except Exception as e:
            logger.error("Error creating loan: {}", e)
            return None

    @staticmethod
    def return_book(loan_id: int) -> tuple[bool, float]:
        try:
            with DatabaseSession() as session:
                loan = session.query(Loan).filter_by(id=loan_id).first()
                if not loan:
                    return False, 0.0

                now = datetime.now()
                loan.data_devolucao_real = now.strftime("%Y-%m-%d")
                loan.status = LOAN_STATUS_RETURNED

                due = datetime.strptime(loan.data_devolucao_prevista, "%Y-%m-%d")
                if now > due:
                    days_late = (now - due).days
                    loan.multa = days_late * FINE_PER_DAY
                    logger.info("Book returned late: {} days, fine: {}", days_late, loan.multa)
                else:
                    loan.multa = 0.0

                return True, loan.multa
        except Exception as e:
            logger.error("Error returning loan: {}", e)
            return False, 0.0

    @staticmethod
    def read_all(status: Optional[str] = None) -> list[dict]:
        try:
            with DatabaseSession() as session:
                query = session.query(Loan)
                if status:
                    query = query.filter_by(status=status)
                loans = query.order_by(Loan.id.desc()).all()
                result = []
                for l in loans:
                    book = session.query(Book).filter_by(id=l.book_id).first()
                    reader = session.query(Reader).filter_by(id=l.reader_id).first()
                    result.append({
                        "id": l.id,
                        "livro": book.titulo if book else "?",
                        "leitor": reader.nome if reader else "?",
                        "data_emprestimo": l.data_emprestimo,
                        "data_devolucao_prevista": l.data_devolucao_prevista,
                        "data_devolucao_real": l.data_devolucao_real or "",
                        "status": l.status,
                        "multa": l.multa,
                        "observacoes": l.observacoes or "",
                    })
                return result
        except Exception as e:
            logger.error("Error reading loans: {}", e)
            return []

    @staticmethod
    def delete(loan_id: int) -> bool:
        try:
            with DatabaseSession() as session:
                loan = session.query(Loan).filter_by(id=loan_id).first()
                if not loan:
                    return False
                session.delete(loan)
                return True
        except Exception as e:
            logger.error("Error deleting loan: {}", e)
            return False

    @staticmethod
    def update_overdue():
        try:
            with DatabaseSession() as session:
                now = datetime.now().strftime("%Y-%m-%d")
                session.query(Loan).filter(
                    Loan.status == LOAN_STATUS_ACTIVE,
                    Loan.data_devolucao_prevista < now,
                ).update({Loan.status: LOAN_STATUS_OVERDUE})
                logger.info("Overdue loans updated")
        except Exception as e:
            logger.error("Error updating overdue: {}", e)

    @staticmethod
    def count() -> int:
        try:
            with DatabaseSession() as session:
                return session.query(Loan).filter_by(status=LOAN_STATUS_ACTIVE).count()
        except Exception:
            return 0

    @staticmethod
    def get_stats() -> dict:
        try:
            with DatabaseSession() as session:
                active = session.query(Loan).filter_by(status=LOAN_STATUS_ACTIVE).count()
                returned = session.query(Loan).filter_by(status=LOAN_STATUS_RETURNED).count()
                overdue = session.query(Loan).filter_by(status=LOAN_STATUS_OVERDUE).count()
                return {"active": active, "returned": returned, "overdue": overdue}
        except Exception:
            return {"active": 0, "returned": 0, "overdue": 0}
