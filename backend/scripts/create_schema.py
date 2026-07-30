"""Create all tables on the target database from SQLAlchemy models."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import engine
from app.models.base import Base
import app.models  # noqa: ensures all models are imported/registered

Base.metadata.create_all(bind=engine)
print("Schema created.")