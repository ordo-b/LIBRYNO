"""Sistema de promoções estratégicas Premium.

Gerencia quando e como mostrar promoções para o usuário FREE:
- Timer de uso (5 min depois do primeiro login)
- Limite de registros (80% do limite FREE)
- Bloqueio de features Premium
- Pós-importação (teaser)
"""
import time

from PySide6.QtCore import QSettings

from src.auth.session import session
from src.utils.logger import logger
from src.utils.constants import (
    FREE_MAX_BOOKS,
    FREE_MAX_READERS,
    FREE_MAX_COLLABS,
)

# Intervalos de promoção (em segundos)
PROMO_INITIAL_DELAY = 300     # 5 minutos após login
PROMO_COOLDOWN = 600          # 10 minutos entre promoções
PROMO_USAGE_THRESHOLD = 0.8   # 80% do limite FREE


class PremiumPromoManager:
    """Gerencia promoções contextuais do plano Premium."""

    def __init__(self):
        self._settings = QSettings("OrdoB", "Libryno")
        self._login_time = time.time()
        self._last_promo_time = 0.0
        self._shown_initial = False
        self._import_count = 0
        self._promos_shown: list[str] = []

    def reset_session(self):
        """Reseta contadores ao fazer login."""
        self._login_time = time.time()
        self._last_promo_time = 0.0
        self._shown_initial = False
        self._import_count = 0
        self._promos_shown = []

    # ─── Checks de quando mostrar promo ───

    def should_show_initial_promo(self) -> bool:
        """Mostra após 5 min de uso (uma única vez)."""
        if session.is_premium:
            return False
        if self._shown_initial:
            return False
        elapsed = time.time() - self._login_time
        if elapsed >= PROMO_INITIAL_DELAY:
            self._shown_initial = True
            return True
        return False

    def should_show_usage_promo(self) -> bool:
        """Mostra quando o usuário atinge 80% de qualquer limite."""
        if session.is_premium:
            return False
        if not self._cooldown_ok():
            return False

        from src.features.books import BooksCRUD
        from src.features.readers import ReadersCRUD
        from src.features.collaborators import CollaboratorsCRUD

        book_count = BooksCRUD.count()
        reader_count = ReadersCRUD.count()
        collab_count = CollaboratorsCRUD.count()

        limits = [
            (book_count, FREE_MAX_BOOKS, "livros"),
            (reader_count, FREE_MAX_READERS, "leitores"),
            (collab_count, FREE_MAX_COLLABS, "colaboradores"),
        ]

        for count, limit, name in limits:
            if limit > 0 and count >= limit * PROMO_USAGE_THRESHOLD:
                self._last_promo_time = time.time()
                return True
        return False

    def should_show_import_teaser(self) -> bool:
        """Mostra após primeira importação bem-sucedida."""
        if session.is_premium:
            return False
        if self._import_count > 0 and self._cooldown_ok():
            return True
        return False

    def register_import(self):
        """Registra que uma importação foi feita."""
        self._import_count += 1

    def should_show_feature_gate(self, feature: str) -> bool:
        """Sempre mostra quando feature premium é bloqueada."""
        if session.is_premium:
            return False
        return True

    # ─── Helpers ───

    def _cooldown_ok(self) -> bool:
        """Verifica se passou tempo suficiente desde a última promo."""
        return (time.time() - self._last_promo_time) >= PROMO_COOLDOWN

    def get_usage_percentage(self) -> dict:
        """Retorna porcentagem de uso de cada limite."""
        if session.is_premium:
            return {"livros": 0, "leitores": 0, "colaboradores": 0}

        from src.features.books import BooksCRUD
        from src.features.readers import ReadersCRUD
        from src.features.collaborators import CollaboratorsCRUD

        return {
            "livros": min(100, int(BooksCRUD.count() / FREE_MAX_BOOKS * 100)),
            "leitores": min(100, int(ReadersCRUD.count() / FREE_MAX_READERS * 100)),
            "colaboradores": min(100, int(CollaboratorsCRUD.count() / FREE_MAX_COLLABS * 100)),
        }

    def get_limit_summary(self) -> str:
        """Retorna resumo dos limites para exibição."""
        if session.is_premium:
            return "Plano Premium — Sem limites ✨"

        from src.features.books import BooksCRUD
        from src.features.readers import ReadersCRUD

        books = BooksCRUD.count()
        readers = ReadersCRUD.count()
        return (
            f"📚 {books}/{FREE_MAX_BOOKS} livros  •  "
            f"👥 {readers}/{FREE_MAX_READERS} leitores  •  "
            f"Plano FREE"
        )


# Instância global
promo_manager = PremiumPromoManager()
