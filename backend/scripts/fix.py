"""Convert absolute source_pdf_path values to repo-relative paths."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import SessionLocal
from app.models import Question

REPO_ROOT = str(Path(__file__).resolve().parents[2])

s = SessionLocal()
fixed = 0
for q in s.query(Question).all():
    if q.source_pdf_path and q.source_pdf_path.startswith("/") and REPO_ROOT in q.source_pdf_path:
        q.source_pdf_path = q.source_pdf_path.split(REPO_ROOT + "/", 1)[1]
        fixed += 1
s.commit()
s.close()
print(f"Fixed {fixed} paths to relative.")