"""Configurações centralizadas do LIBRYNO."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv(BASE_DIR / ".env.example")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


class Config:
    APP_NAME = "LIBRYNO"
    APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
    APP_DEBUG = os.getenv("APP_DEBUG", "false").lower() == "true"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR / 'libryno.db'}",
    )

    ORDOB_API_URL = os.getenv("ORDOB_API_URL", "https://api.ordob.com/api")
    ORDOB_API_URL_DEV = os.getenv("ORDOB_API_URL_DEV", "http://localhost:8000/api")
    ORDOB_PRODUCT_SLUG = os.getenv("ORDOB_PRODUCT_SLUG", "libryno")
    ORDOB_ENV = os.getenv("ORDOB_ENV", "production")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "libryno://auth/callback")

    SYNC_ENABLED = os.getenv("SYNC_ENABLED", "true").lower() == "true"
    SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "300"))  # 5 minutos

    @classmethod
    def get_api_url(cls) -> str:
        if cls.APP_DEBUG:
            return cls.ORDOB_API_URL_DEV
        return cls.ORDOB_API_URL
