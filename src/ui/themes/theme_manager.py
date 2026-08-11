"""Gerenciador de temas visuais com detecção automática do sistema."""
from pathlib import Path

from PySide6 import QtWidgets

from src.utils.logger import logger
from src.utils.system_theme import get_system_theme

THEMES_DIR = Path(__file__).parent
_current_theme = "dark"


def get_available_themes() -> list[str]:
    return [f.stem for f in THEMES_DIR.glob("*.qss")]


def load_theme(name: str) -> str:
    filepath = THEMES_DIR / f"{name}.qss"
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return ""


def apply_theme(app: QtWidgets.QApplication, name: str):
    global _current_theme
    stylesheet = load_theme(name)
    if stylesheet:
        app.setStyleSheet(stylesheet)
        _current_theme = name
        logger.info("Theme applied: {}", name)
    else:
        logger.warning("Theme not found: {}", name)


def get_current_theme() -> str:
    return _current_theme


def cycle_theme(app: QtWidgets.QApplication):
    themes = get_available_themes()
    if not themes:
        return
    idx = themes.index(_current_theme) if _current_theme in themes else 0
    next_idx = (idx + 1) % len(themes)
    apply_theme(app, themes[next_idx])


def apply_system_theme(app: QtWidgets.QApplication):
    """Aplica o tema do sistema operacional automaticamente."""
    system_theme = get_system_theme()
    if system_theme:
        apply_theme(app, system_theme)
    else:
        apply_theme(app, "dark")
