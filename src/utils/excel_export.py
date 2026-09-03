"""Exportação de dados para Excel.

FREE tier: até FREE_MAX_EXPORTS_PER_DAY exportações por dia.
"""
from pathlib import Path

import pandas as pd

from src.auth.session import session
from src.features.books import BooksCRUD
from src.features.readers import ReadersCRUD
from src.utils.constants import FREE_MAX_EXPORTS_PER_DAY
from src.utils.logger import logger
from src.utils.rate_limiter import export_rate_limiter


def _check_export_allowed(export_type: str = "excel") -> bool:
    """Verifica se o usuário pode exportar (FREE tier check)."""
    if session.is_premium:
        return True

    if not export_rate_limiter.can_export(export_type, FREE_MAX_EXPORTS_PER_DAY):
        remaining = export_rate_limiter.get_remaining(export_type, FREE_MAX_EXPORTS_PER_DAY)
        logger.warning(
            "FREE tier export limit reached (0/{})",
            FREE_MAX_EXPORTS_PER_DAY,
        )
        return False
    return True


def export_books_to_excel(filepath: str) -> bool:
    if not _check_export_allowed("excel"):
        return False

    try:
        data = BooksCRUD.read_all()
        if not data:
            return False
        df = pd.DataFrame(data)
        df.to_excel(filepath, sheet_name="Livros", index=False)
        export_rate_limiter.record_export("excel")
        logger.info("Books exported to: {}", filepath)
        return True
    except Exception as e:
        logger.error("Error exporting books: {}", e)
        return False


def export_readers_to_excel(filepath: str) -> bool:
    if not _check_export_allowed("excel"):
        return False

    try:
        data = ReadersCRUD.read_all()
        if not data:
            return False
        df = pd.DataFrame(data)
        df.to_excel(filepath, sheet_name="Leitores", index=False)
        export_rate_limiter.record_export("excel")
        logger.info("Readers exported to: {}", filepath)
        return True
    except Exception as e:
        logger.error("Error exporting readers: {}", e)
        return False


def export_all_to_excel(directory: str) -> bool:
    if not _check_export_allowed("excel"):
        return False

    try:
        out_dir = Path(directory)
        out_dir.mkdir(parents=True, exist_ok=True)
        books_ok = export_books_to_excel(str(out_dir / "livros.xlsx"))
        readers_ok = export_readers_to_excel(str(out_dir / "leitores.xlsx"))
        return books_ok or readers_ok
    except Exception as e:
        logger.error("Error exporting all: {}", e)
        return False
