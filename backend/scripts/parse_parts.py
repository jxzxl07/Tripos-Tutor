"""
Splits each question into its shared context + ordered parts (a, b, c...) using
the LLM, and stores them. Idempotent: skips questions already parsed.
"""
import json, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import SessionLocal
from app.models import Question, QuestionPart
from app.services.llm import client, FLASH

WORKERS = 5   # lower than 10 to reduce read-timeouts on the larger parsing prompts


class Part(BaseModel):
    label: str          # "a", "b", ... (or "main" if the question has no sub-parts)
    text: str
    marks: int | None

class ParsedQuestion(BaseModel):
    context: str        # shared preamble before the parts (empty string if none)
    parts: list[Part]


PROMPT = """Split this Cambridge Tripos exam question into its structure.
Return: the shared CONTEXT (any preamble/setup before the sub-parts — empty string
if none), and an ordered list of PARTS. Each part has a label (a, b, c...), its full
text, and its marks if stated. If the question has NO sub-parts, return a single part
with label "main" containing the whole question. Preserve all technical content exactly.

QUESTION:
{question}
"""


def clean(s: str) -> str:
    """Strip NUL bytes Postgres can't store."""
    return (s or "").replace("\x00", "")


def parse_one(q_id, question_text, max_retries=3):
    prompt = PROMPT.format(question=question_text)
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=FLASH,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ParsedQuestion,
                    "http_options": {"timeout": 60000},
                },
            )
            return (q_id, resp.parsed)
        except Exception as e:
            if any(x in str(e) for x in ("503", "UNAVAILABLE", "429", "timeout", "Deadline", "timed out")):
                time.sleep(2 * (attempt + 1)); continue
            print(f"  ! failed q{q_id}: {e}")
            return (q_id, None)
    print(f"  ! gave up q{q_id} (transient) — re-run to retry")
    return (q_id, None)


def main():
    session = SessionLocal()
    todo = []
    for q in session.query(Question).all():
        if session.query(QuestionPart).filter_by(question_id=q.id).first():
            continue          # already parsed
        todo.append((q.id, q.question_text))

    print(f"Parsing {len(todo)} questions into parts with {WORKERS} workers...")
    done = failed = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(parse_one, qid, text) for qid, text in todo]
        for fut in as_completed(futures):
            q_id, parsed = fut.result()
            if parsed is None:
                failed += 1
                continue
            q = session.get(Question, q_id)
            q.context_text = clean(parsed.context) or None
            for i, p in enumerate(parsed.parts):
                session.add(QuestionPart(
                    question_id=q_id,
                    label=clean(p.label)[:10],
                    order_index=i,
                    part_text=clean(p.text),
                    marks=p.marks,
                ))
            session.commit()
            done += 1
            print(f"  + q{q_id}: {len(parsed.parts)} part(s)")

    session.close()
    print(f"\nDone. parsed={done} failed={failed}")


if __name__ == "__main__":
    main()