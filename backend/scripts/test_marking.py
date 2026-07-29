"""Quick manual test: mark a sample answer against a real question's rubric."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import Question, Rubric
from app.services.marking import mark_answer

session = SessionLocal()

# grab the first question that has a rubric
rubric = session.query(Rubric).first()
q = session.query(Question).get(rubric.question_id)
criteria = json.loads(rubric.criteria_json)

print(f"QUESTION ({q.course.slug} {q.year} p{q.paper}q{q.question_number}):")
print(q.question_text[:600], "...\n")

# a deliberately partial answer, so we can see it distinguish scored vs missed
sample_answer = input("Type a sample answer (or press Enter for a weak default):\n") \
    or "I think the answer involves grammars and parsing but I'm not sure of the details."

result = mark_answer(q.question_text, criteria, rubric.total_marks, sample_answer)

print(f"\n=== MARK: {result.total_awarded} / {result.total_available} ===")
print(f"\nSTRENGTHS (what scored):\n{result.strengths}")
print(f"\nGAPS (what was missed):\n{result.gaps}")
print(f"\nOVERALL:\n{result.overall_feedback}")

session.close()