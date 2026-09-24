import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Question, QuestionPart, Rubric, Attempt, User
from app.security import get_current_user
from app.services.marking import mark_part
from app.services.sanitize import MAX_ANSWER_CHARS

router = APIRouter(prefix="/api", tags=["marking"])


class MarkRequest(BaseModel):
    part_id: int
    # Length cap bounds LLM cost per request; no user_id — it comes from the token.
    answer: str = Field(max_length=MAX_ANSWER_CHARS)


@router.post("/mark")
def mark(req: MarkRequest,
         user: User = Depends(get_current_user),
         db: Session = Depends(get_db)):
    part = db.get(QuestionPart, req.part_id)
    if not part:
        raise HTTPException(404, "Part not found")

    q = db.get(Question, part.question_id)
    rubric = db.query(Rubric).filter_by(question_id=q.id).first()
    criteria = json.loads(rubric.criteria_json) if rubric else []

    result = mark_part(
        part.label, part.part_text, part.marks,
        criteria, req.answer, q.context_text,
    )

    attempt = Attempt(
        user_id=user.id,
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
    )   # created_at is set by the database (server_default=now())
    db.add(attempt)
    db.commit()
    return result.model_dump()
