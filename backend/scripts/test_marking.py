"""Manual test: mark a sample answer to one part of a question."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import Question, QuestionPart, Rubric
from app.services.marking import mark_part

session = SessionLocal()

# use q35 (Compiler Construction) — we know its parts and rubric are clean
q = session.get(Question, 35)
parts = session.query(QuestionPart).filter_by(question_id=35).order_by(QuestionPart.order_index).all()
rubric = session.query(Rubric).filter_by(question_id=35).first()
criteria = json.loads(rubric.criteria_json)

# mark part (a)
part = parts[0]
print(f"CONTEXT: {q.context_text or '(none)'}\n")
print(f"PART ({part.label}) [{part.marks} marks]: {part.part_text}\n")

sample = input("Type an answer for this part (Enter for a weak default):\n") \
    or "I think you write lambda n n or something like that."

result = mark_part(part.label, part.part_text, part.marks, criteria, sample, q.context_text)

print(f"\n=== {result.marks_awarded} / {result.marks_available} ===")
print(f"\nSTRENGTHS: {result.strengths}")
print(f"\nGAPS: {result.gaps}")
print(f"\nFEEDBACK: {result.feedback}")

session.close()