from sqlalchemy import text

from app.core.database import engine


def _db_up() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        return False
    return True


def test_ready_reflects_db_state(client):
    r = client.get("/ready")
    if _db_up():
        assert r.status_code == 200
        assert r.json() == {"status": "ready", "database": "connected"}
    else:
        assert r.status_code == 503
        assert r.json() == {"status": "not_ready", "database": "unavailable"}
