import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import SessionLocal
from app.models import Question, QuestionPart, Rubric
from app.services.marking import mark_part

router = APIRouter(prefix="/api", tags=["marking"])


class MarkRequest(BaseModel):
    part_id: int
    answer: str


@router.post("/mark")
def mark(req: MarkRequest):
    s = SessionLocal()
    part = s.get(QuestionPart, req.part_id)
    if not part:
        s.close()
        raise HTTPException(404, "Part not found")

    q = s.get(Question, part.question_id)
    rubric = s.query(Rubric).filter_by(question_id=q.id).first()
    criteria = json.loads(rubric.criteria_json) if rubric else []

    result = mark_part(
        part.label, part.part_text, part.marks,
        criteria, req.answer, q.context_text,
    )
    s.close()
    return result.model_dump()