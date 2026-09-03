"""Rate limiter para FREE tier — exportações diárias."""
import json
from datetime import date
from pathlib import Path

from src.config import DATA_DIR
from src.utils.logger import logger

_RATE_FILE = DATA_DIR / ".export_count"


class ExportRateLimiter:
    """Controla quantas exportações o usuário FREE pode fazer por dia."""

    def __init__(self):
        self._counts: dict[str, int] = {}
        self._load()

    def _load(self):
        try:
            if _RATE_FILE.exists():
                data = json.loads(_RATE_FILE.read_text(encoding="utf-8"))
                if data.get("date") == date.today().isoformat():
                    self._counts = data.get("counts", {})
                else:
                    # Dia diferente → resetar contadores
                    self._counts = {}
        except Exception:
            self._counts = {}

    def _save(self):
        try:
            data = {
                "date": date.today().isoformat(),
                "counts": self._counts,
            }
            _RATE_FILE.write_text(json.dumps(data), encoding="utf-8")
        except Exception as e:
            logger.error("Failed to save rate limit: {}", e)

    def can_export(self, export_type: str, max_per_day: int) -> bool:
        """Verifica se o usuário pode fazer mais uma exportação hoje."""
        current = self._counts.get(export_type, 0)
        return current < max_per_day

    def record_export(self, export_type: str):
        """Registra uma exportação realizada."""
        self._counts[export_type] = self._counts.get(export_type, 0) + 1
        self._save()
        logger.debug("Export recorded: {} (count: {})", export_type, self._counts[export_type])

    def get_remaining(self, export_type: str, max_per_day: int) -> int:
        """Retorna quantas exportações restam hoje."""
        current = self._counts.get(export_type, 0)
        return max(0, max_per_day - current)


export_rate_limiter = ExportRateLimiter()
