"""
Marking eval harness: runs the marking engine over labelled test cases and
reports how often the awarded mark falls within the expected range, plus
mean absolute error. Measures marking accuracy.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.db import SessionLocal
from app.models import QuestionPart, Rubric, Question
from app.services.marking import mark_part

CASES = json.loads((Path(__file__).parent / "marking_cases.json").read_text())


def resolve_part(session, case):
    """Find the QuestionPart for a case by question_id + part_label."""
    return (
        session.query(QuestionPart)
        .filter_by(question_id=case["question_id"], label=case["part_label"])
        .first()
    )


def run():
    session = SessionLocal()
    results = []

    for case in CASES:
        part = resolve_part(session, case)
        if not part:
            print(f"  ! SKIP {case['name']}: part not found")
            continue

        q = session.get(Question, part.question_id)
        rubric = session.query(Rubric).filter_by(question_id=q.id).first()
        criteria = json.loads(rubric.criteria_json) if rubric else []

        marked = mark_part(part.label, part.part_text, part.marks,
                           criteria, case["answer"], q.context_text)
        awarded = marked.marks_awarded
        lo, hi = case["expected_min"], case["expected_max"]
        in_range = lo <= awarded <= hi
        # error = distance from the nearest edge of the expected band
        err = 0 if in_range else min(abs(awarded - lo), abs(awarded - hi))

        results.append({"name": case["name"], "awarded": awarded,
                        "expected": f"{lo}-{hi}", "in_range": in_range, "err": err})
        mark = "✓" if in_range else "✗"
        print(f"  {mark} {case['name']}: got {awarded}, expected {lo}-{hi}")

    session.close()

    n = len(results)
    passed = sum(r["in_range"] for r in results)
    mae = sum(r["err"] for r in results) / n if n else 0
    print(f"\n=== Marking accuracy: {passed}/{n} within expected range "
          f"({100*passed//n if n else 0}%) | mean abs error: {mae:.2f} marks ===")
    return results, passed, n


if __name__ == "__main__":
    run()