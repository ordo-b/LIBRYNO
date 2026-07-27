"""Gerenciamento de idiomas (i18n)."""
import json
import os
from pathlib import Path
from src.utils.logger import logger

I18N_DIR = Path(__file__).parent
_locales: dict[str, dict] = {}
_current_locale = os.getenv("APP_LOCALE", "pt_BR")


def _load_locale(locale: str):
    filepath = I18N_DIR / f"{locale}.json"
    if filepath.exists():
        _locales[locale] = json.loads(filepath.read_text(encoding="utf-8"))
    else:
        logger.warning("Locale not found: {}", locale)


def set_locale(locale: str):
    global _current_locale
    if locale not in _locales:
        _load_locale(locale)
    if locale in _locales:
        _current_locale = locale
        logger.info("Locale set to: {}", locale)


def t(key: str, **kwargs) -> str:
    """Traduz uma chave de texto. Ex: t('login.title')"""
    if _current_locale not in _locales:
        _load_locale(_current_locale)
        _load_locale("pt_BR")

    data = _locales.get(_current_locale, _locales.get("pt_BR", {}))

    parts = key.split(".")
    value = data
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part, key)
        else:
            return key

    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, IndexError):
            return value
    return value if isinstance(value, str) else key


def get_available_locales() -> list[str]:
    return [f.stem for f in I18N_DIR.glob("*.json")]


def get_current_locale() -> str:
    return _current_locale
