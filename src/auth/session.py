"""Gerenciamento de sessão e token do usuário."""
import json
from pathlib import Path
from typing import Optional
from src.config import DATA_DIR
from src.utils.logger import logger

SESSION_FILE = DATA_DIR / ".session"


class Session:
    def __init__(self):
        self._token: Optional[str] = None
        self._user: Optional[dict] = None
        self._premium: bool = False
        self._license_key: Optional[str] = None
        self._load_session()

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None

    @property
    def is_premium(self) -> bool:
        return self._premium

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def user(self) -> Optional[dict]:
        return self._user

    @property
    def user_name(self) -> str:
        if self._user:
            return self._user.get("name", "")
        return ""

    @property
    def user_email(self) -> str:
        if self._user:
            return self._user.get("email", "")
        return ""

    @property
    def license_key(self) -> Optional[str]:
        return self._license_key

    def login(self, token: str, user: dict):
        self._token = token
        self._user = user
        self._save_session()
        logger.info("Session started for: {}", user.get("name", "unknown"))

    def set_premium(self, premium: bool, license_key: str = ""):
        self._premium = premium
        self._license_key = license_key
        self._save_session()
        logger.info("Premium status set: {}", premium)

    def logout(self):
        self._token = None
        self._user = None
        self._premium = False
        self._license_key = None
        self._clear_session_file()
        logger.info("Session ended")

    def _save_session(self):
        try:
            data = {
                "token": self._token,
                "user": self._user,
                "premium": self._premium,
                "license_key": self._license_key,
            }
            SESSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error("Failed to save session: {}", e)

    def _load_session(self):
        try:
            if SESSION_FILE.exists():
                data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
                self._token = data.get("token")
                self._user = data.get("user")
                self._premium = data.get("premium", False)
                self._license_key = data.get("license_key")
                if self._token:
                    logger.debug("Session restored for: {}", self.user_name)
        except Exception as e:
            logger.warning("Failed to load session: {}", e)

    def _clear_session_file(self):
        try:
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
        except Exception as e:
            logger.warning("Failed to clear session file: {}", e)


session = Session()
