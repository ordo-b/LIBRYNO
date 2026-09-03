"""Testes para CollaboratorsCRUD free tier limit e rate limiter."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base


@pytest.fixture(autouse=True)
def patch_database(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    import src.core.database as db_mod
    monkeypatch.setattr(db_mod, "_engine", engine)
    monkeypatch.setattr(db_mod, "_SessionLocal", TestSession)

    yield engine


# ─── COLLABORATORS FREE TIER ─────────────────────────────────

def test_collab_free_tier_limit():
    from src.features.collaborators import CollaboratorsCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_COLLABORATORS

    was_premium = session.is_premium
    session._premium = False
    session._license_key = None

    for i in range(FREE_MAX_COLLABORATORS):
        result = CollaboratorsCRUD.create(
            nome=f"Colab {i}", nome_usuario=f"colab{i}", senha="12345"
        )
        assert result is not None

    # Próximo deve falhar
    result = CollaboratorsCRUD.create(
        nome="Extra", nome_usuario="extra", senha="12345"
    )
    assert result is None
    assert CollaboratorsCRUD.count() == FREE_MAX_COLLABORATORS

    session._premium = was_premium


def test_collab_premium_unlimited():
    from src.features.collaborators import CollaboratorsCRUD
    from src.auth.session import session
    from src.utils.constants import FREE_MAX_COLLABORATORS

    was_premium = session.is_premium
    session._premium = True
    session._license_key = "KEY"

    for i in range(FREE_MAX_COLLABORATORS + 5):
        result = CollaboratorsCRUD.create(
            nome=f"Colab {i}", nome_usuario=f"colab{i}", senha="12345"
        )
        assert result is not None

    assert CollaboratorsCRUD.count() == FREE_MAX_COLLABORATORS + 5

    session._premium = was_premium


# ─── EXPORT RATE LIMITER ──────────────────────────────────────

def test_export_rate_limiter_allows_initial(monkeypatch, tmp_path):
    monkeypatch.setattr("src.utils.rate_limiter._RATE_FILE", tmp_path / ".export_count")
    from src.utils.rate_limiter import ExportRateLimiter
    limiter = ExportRateLimiter()

    assert limiter.can_export("excel", 3) is True
    assert limiter.get_remaining("excel", 3) == 3


def test_export_rate_limiter_blocks_after_limit(monkeypatch, tmp_path):
    monkeypatch.setattr("src.utils.rate_limiter._RATE_FILE", tmp_path / ".export_count")
    from src.utils.rate_limiter import ExportRateLimiter
    limiter = ExportRateLimiter()

    for _ in range(3):
        limiter.record_export("excel")

    assert limiter.can_export("excel", 3) is False
    assert limiter.get_remaining("excel", 3) == 0


def test_export_rate_limiter_resets_next_day(monkeypatch, tmp_path):
    monkeypatch.setattr("src.utils.rate_limiter._RATE_FILE", tmp_path / ".export_count")
    from src.utils.rate_limiter import ExportRateLimiter

    # Simular dados de ontem
    import json
    from datetime import date, timedelta
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    (tmp_path / ".export_count").write_text(json.dumps({
        "date": yesterday, "counts": {"excel": 5}
    }))

    limiter = ExportRateLimiter()
    # Deve resetar porque a data mudou
    assert limiter.can_export("excel", 3) is True
    assert limiter.get_remaining("excel", 3) == 3
