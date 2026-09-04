import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Default: unreachable DB so /ready reliably fails and DB tests can auto-skip.
# Set real DATABASE_* env vars (e.g. by exporting them or via docker compose)
# to run the DB-dependent tests.
os.environ.setdefault("DATABASE_HOST", "127.0.0.1")
os.environ.setdefault("DATABASE_PORT", "1")
os.environ.setdefault("DATABASE_NAME", "test")
os.environ.setdefault("DATABASE_USER", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.database import engine  # noqa: E402
from app.main import app  # noqa: E402


def _database_available() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        return False
    return True


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def requires_db() -> None:
    if not _database_available():
        pytest.skip("PostgreSQL not reachable; skipping DB-dependent test.")
