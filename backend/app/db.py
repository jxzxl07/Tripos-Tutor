from collections.abc import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.config import settings

# The web app uses an async driver (+asyncpg); scripts use plain sync psycopg2.
# Strip +asyncpg so this one connection string works for both.
sync_url = settings.database_url.replace("+asyncpg", "")
engine = create_engine(sync_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request, always closed —
    even if the route raises (the old pattern leaked sessions on errors)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
