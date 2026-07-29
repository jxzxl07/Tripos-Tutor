"""
Walks data/papers/<Course>/<Year>/, extracts text from each question PDF
(and its mark scheme, if present), and loads them into Postgres.

Idempotent: re-running only fills in what's missing.
"""
import re
import sys
from pathlib import Path
import fitz  # PyMuPDF (package is 'pymupdf', import name is 'fitz')

# Make 'from app...' imports work no matter which directory we run from
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import Course, Question, MarkScheme

PAPERS_DIR = Path(__file__).resolve().parents[2] / "data" / "papers"
QUESTION_RE = re.compile(r"^p(\d+)q(\d+)\.pdf$")        # p5q7.pdf
MARKSCHEME_SUFFIX = "ms.pdf"                             # p5q7ms.pdf


def extract_text(pdf_path: Path) -> str:
    """Pull all text from a PDF, stripping NUL bytes Postgres can't store."""
    with fitz.open(pdf_path) as doc:
        text = "\n\n".join(page.get_text() for page in doc)
    return text.replace("\x00", "").strip()      # NUL bytes crash the DB insert


def get_or_create_course(session, slug: str) -> Course:
    course = session.query(Course).filter_by(slug=slug).first()
    if course is None:
        course = Course(slug=slug, name=slug.replace("-", " "))
        session.add(course)
        session.flush()          # get course.id without committing yet
    return course


def main():
    if not PAPERS_DIR.exists():
        print(f"No data at {PAPERS_DIR}")
        return

    created = skipped = ms_created = 0
    session = SessionLocal()

    for course_dir in sorted(p for p in PAPERS_DIR.iterdir() if p.is_dir()):
        course = get_or_create_course(session, course_dir.name)

        for year_dir in sorted(p for p in course_dir.iterdir() if p.is_dir()):
            if not year_dir.name.isdigit():
                continue
            year = int(year_dir.name)

            for pdf in sorted(year_dir.glob("*.pdf")):
                m = QUESTION_RE.match(pdf.name)
                if not m:
                    continue          # mark schemes handled via their question
                paper, qnum = int(m.group(1)), int(m.group(2))

                question = session.query(Question).filter_by(
                    course_id=course.id, year=year,
                    paper=paper, question_number=qnum,
                ).first()

                if question is None:
                    question = Question(
                        course_id=course.id, year=year, paper=paper,
                        question_number=qnum,
                        question_text=extract_text(pdf),
                        source_pdf_path=str(pdf),
                    )
                    session.add(question)
                    session.flush()
                    created += 1
                    print(f"  + {course_dir.name}/{year}/p{paper}q{qnum}")
                else:
                    skipped += 1

                # attach mark scheme if a sibling exists and we don't have one
                ms_path = pdf.with_name(f"p{paper}q{qnum}{MARKSCHEME_SUFFIX}")
                if ms_path.exists() and question.mark_scheme is None:
                    session.add(MarkScheme(
                        question_id=question.id,
                        scheme_text=extract_text(ms_path),
                        source_pdf_path=str(ms_path),
                    ))
                    ms_created += 1

        session.commit()            # commit once per course

    session.close()
    print(f"\nDone. questions created={created} skipped(existing)={skipped} "
          f"mark_schemes created={ms_created}")


if __name__ == "__main__":
    main()