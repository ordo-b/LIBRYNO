"""Gerenciamento de sessão e token do usuário."""
import hashlib
import hmac
import json
import os

from src.config import DATA_DIR
from src.utils.logger import logger

SESSION_FILE = DATA_DIR / ".session"

# Chave derivada do ambiente para assinatura HMAC
_HMAC_KEY = os.environ.get(
    "LIBRYNO_SESSION_KEY",
    "libryno-default-session-key-do-not-use-in-prod",
).encode()


def _sign(data: dict) -> str:
    """Gera assinatura HMAC-SHA256 dos dados da sessão."""
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hmac.new(_HMAC_KEY, payload.encode(), hashlib.sha256).hexdigest()


class Session:
    def __init__(self):
        self._token: str | None = None
        self._user: dict | None = None
        self._premium: bool = False
        self._license_key: str | None = None
        self._load_session()

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None

    @property
    def is_premium(self) -> bool:
        return self._premium

    @property
    def token(self) -> str | None:
        return self._token

    @property
    def user(self) -> dict | None:
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
    def license_key(self) -> str | None:
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
            # Salvar com assinatura HMAC para detectar adulteração
            signed = {
                "payload": data,
                "sig": _sign(data),
            }
            SESSION_FILE.write_text(
                json.dumps(signed, indent=2), encoding="utf-8"
            )
        except Exception as e:
            logger.error("Failed to save session: {}", e)

    def _load_session(self):
        try:
            if SESSION_FILE.exists():
                raw = json.loads(SESSION_FILE.read_text(encoding="utf-8"))

                # Formato novo: com assinatura HMAC
                if "payload" in raw and "sig" in raw:
                    payload = raw["payload"]
                    expected_sig = _sign(payload)
                    if not hmac.compare_digest(raw["sig"], expected_sig):
                        logger.warning(
                            "Session file TAMPERED — discarding session"
                        )
                        self._clear_session_file()
                        return
                else:
                    # Formato antigo (sem assinatura) — aceitar mas re-salvar
                    payload = raw

                self._token = payload.get("token")
                self._user = payload.get("user")
                self._premium = payload.get("premium", False)
                self._license_key = payload.get("license_key")
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
