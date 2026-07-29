from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# The web app uses an async driver (+asyncpg); scripts use plain sync psycopg2.
# Strip +asyncpg so this one connection string works for both.
sync_url = settings.database_url.replace("+asyncpg", "")
engine = create_engine(sync_url)
SessionLocal = sessionmaker(bind=engine)
