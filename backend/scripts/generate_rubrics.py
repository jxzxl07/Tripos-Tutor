"""
For every question without a rubric, generate a structured marking rubric
with Gemini and store it. Runs requests concurrently for speed.
Idempotent: skips questions that already have a rubric.
"""
import json
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import Question, Rubric
from app.services.llm import client, FLASH

WORKERS = 10   # how many requests in flight at once


class Criterion(BaseModel):
    point: str
    marks: int

class RubricOut(BaseModel):
    total_marks: int
    criteria: list[Criterion]


PROMPT = """You are a Cambridge Computer Science Tripos examiner.
Produce a concise marking rubric for the exam question below: the key points a
strong answer must cover, and the marks each is worth. Tripos questions are
typically out of 20 marks. Base the rubric on the question{scheme_note}.

QUESTION:
{question}
{scheme}
"""


def build_prompt(question_text, scheme_text):
    if scheme_text:
        return PROMPT.format(
            question=question_text,
            scheme_note=" and the official mark scheme provided",
            scheme=f"\nOFFICIAL MARK SCHEME (ground your rubric in this):\n{scheme_text}",
        )
    return PROMPT.format(question=question_text, scheme_note="", scheme="")


def generate_one(q_id, prompt, has_scheme, max_retries=3):
    """Call Gemini for one question; retry on transient errors. Returns a dict or None."""
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=FLASH,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": RubricOut,
                    "http_options": {"timeout": 30000},
                },
            )
            r = resp.parsed
            return {
                "question_id": q_id,
                "total_marks": r.total_marks,
                "criteria_json": json.dumps([c.model_dump() for c in r.criteria]),
                "grounded_in_scheme": has_scheme,
            }
        except Exception as e:
            if any(x in str(e) for x in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "timeout", "Deadline")):
                time.sleep(2 * (attempt + 1))
                continue
            print(f"  ! failed q{q_id}: {e}")
            return None
    print(f"  ! gave up q{q_id} (transient) — re-run to retry")
    return None


def main():
    session = SessionLocal()

    # build the list of work up front (questions without a rubric)
    todo = []
    for q in session.query(Question).all():
        if session.query(Rubric).filter_by(question_id=q.id).first():
            continue
        scheme_text = q.mark_scheme.scheme_text if q.mark_scheme else None
        todo.append((q.id, build_prompt(q.question_text, scheme_text), scheme_text is not None))

    print(f"Generating {len(todo)} rubrics with {WORKERS} workers...")
    made = failed = 0

    # fire requests concurrently
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(generate_one, qid, prompt, hs): qid for qid, prompt, hs in todo}
        for fut in as_completed(futures):
            result = fut.result()
            if result is None:
                failed += 1
                continue
            session.add(Rubric(**result))
            session.commit()
            made += 1
            print(f"  + q{result['question_id']} done ({made}/{len(todo)})")

    session.close()
    print(f"\nDone. rubrics created={made} failed={failed}")


if __name__ == "__main__":
    main()