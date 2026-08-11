"""Configuração de logging com loguru."""
import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()

log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

logger.add(sys.stderr, format=log_format, level="INFO", colorize=True)

logger.add(
    LOG_DIR / "libryno_{time:YYYY-MM-DD}.log",
    format=log_format,
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
)
