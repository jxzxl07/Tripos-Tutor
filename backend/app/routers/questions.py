import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import SessionLocal
from app.models import Question, QuestionPart, Course

router = APIRouter(prefix="/api", tags=["questions"])


class PartOut(BaseModel):
    id: int
    label: str
    part_text: str
    marks: int | None

class QuestionOut(BaseModel):
    id: int
    course: str
    year: int
    paper: int
    question_number: int
    context_text: str | None
    parts: list[PartOut]


@router.get("/courses")
def list_courses():
    s = SessionLocal()
    courses = s.query(Course).order_by(Course.name).all()
    out = [{"id": c.id, "name": c.name, "slug": c.slug} for c in courses]
    s.close()
    return out


@router.get("/questions/{question_id}", response_model=QuestionOut)
def get_question(question_id: int):
    s = SessionLocal()
    q = s.get(Question, question_id)
    if not q:
        s.close()
        raise HTTPException(404, "Question not found")
    parts = s.query(QuestionPart).filter_by(question_id=q.id)\
        .order_by(QuestionPart.order_index).all()
    result = QuestionOut(
        id=q.id, course=q.course.slug, year=q.year, paper=q.paper,
        question_number=q.question_number, context_text=q.context_text,
        parts=[PartOut(id=p.id, label=p.label, part_text=p.part_text, marks=p.marks) for p in parts],
    )
    s.close()
    return result

@router.get("/courses/{slug}/questions")
def questions_for_course(slug: str):
    s = SessionLocal()
    course = s.query(Course).filter_by(slug=slug).first()
    if not course:
        s.close()
        raise HTTPException(404, "Course not found")
    qs = s.query(Question).filter_by(course_id=course.id)\
        .order_by(Question.year.desc(), Question.paper, Question.question_number).all()
    out = [{"id": q.id, "year": q.year, "paper": q.paper, "question_number": q.question_number} for q in qs]
    s.close()
    return out

from fastapi.responses import FileResponse
import os

@router.get("/questions/{question_id}/pdf")
def get_question_pdf(question_id: int):
    s = SessionLocal()
    q = s.get(Question, question_id)
    s.close()
    if not q or not q.source_pdf_path:
        raise HTTPException(404, "PDF not found")
    if not os.path.exists(q.source_pdf_path):
        raise HTTPException(404, "PDF file missing on disk")
    return FileResponse(q.source_pdf_path, media_type="application/pdf")


