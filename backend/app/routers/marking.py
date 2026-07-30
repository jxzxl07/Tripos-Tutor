import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import SessionLocal
from app.models import Question, QuestionPart, Rubric, Attempt
from app.services.marking import mark_part

router = APIRouter(prefix="/api", tags=["marking"])


class MarkRequest(BaseModel):
    part_id: int
    answer: str
    user_id: int


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

    attempt = Attempt(
        user_id=req.user_id,
        question_id=q.id,
        answer_text=req.answer,
        awarded_mark=result.marks_awarded,
        feedback_json=json.dumps({
            "part_label": part.label,
            "part_id": part.id,
            "marks_awarded": result.marks_awarded,
            "marks_available": result.marks_available,
            "strengths": result.strengths,
            "gaps": result.gaps,
            "feedback": result.feedback,
        }),
        created_at=datetime.utcnow(),
    )
    s.add(attempt)
    s.commit()
    s.close()
    return result.model_dump()