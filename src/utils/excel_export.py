"""Exportação de dados para Excel."""
from pathlib import Path
import pandas as pd
from src.utils.logger import logger
from src.features.books import BooksCRUD
from src.features.readers import ReadersCRUD


def export_books_to_excel(filepath: str) -> bool:
    try:
        data = BooksCRUD.read_all()
        if not data:
            return False
        df = pd.DataFrame(data)
        df.to_excel(filepath, sheet_name="Livros", index=False)
        logger.info("Books exported to: {}", filepath)
        return True
    except Exception as e:
        logger.error("Error exporting books: {}", e)
        return False


def export_readers_to_excel(filepath: str) -> bool:
    try:
        data = ReadersCRUD.read_all()
        if not data:
            return False
        df = pd.DataFrame(data)
        df.to_excel(filepath, sheet_name="Leitores", index=False)
        logger.info("Readers exported to: {}", filepath)
        return True
    except Exception as e:
        logger.error("Error exporting readers: {}", e)
        return False


def export_all_to_excel(directory: str) -> bool:
    try:
        out_dir = Path(directory)
        out_dir.mkdir(parents=True, exist_ok=True)
        books_ok = export_books_to_excel(str(out_dir / "livros.xlsx"))
        readers_ok = export_readers_to_excel(str(out_dir / "leitores.xlsx"))
        return books_ok or readers_ok
    except Exception as e:
        logger.error("Error exporting all: {}", e)
        return False
