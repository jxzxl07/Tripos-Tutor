import json
from fastapi import APIRouter
from app.db import SessionLocal
from app.models import Attempt, Question, Course, ImprovementSummary
from app.services.llm import client, FLASH

router = APIRouter(prefix="/api", tags=["dashboard"])


SUMMARY_PROMPT = """You are a Cambridge CS tutor. A student has attempted several
exam questions in the course "{course}". Below are the gaps and feedback from their
marked answers. Synthesise these into a concise, prioritised list of what they should
focus on improving in this course. Be specific and actionable. 3-5 points.

FEEDBACK FROM THEIR ATTEMPTS:
{feedback}
"""


def generate_summary(course_name, feedback_items):
    joined = "\n\n".join(feedback_items)
    prompt = SUMMARY_PROMPT.format(course=course_name, feedback=joined)
    resp = client.models.generate_content(
        model=FLASH,
        contents=prompt,
        config={"http_options": {"timeout": 30000}},
    )
    return resp.text


@router.get("/dashboard/{user_id}")
def dashboard(user_id: int):
    s = SessionLocal()

    # all attempts for this user, joined to their course
    rows = (
        s.query(Attempt, Question, Course)
        .join(Question, Attempt.question_id == Question.id)
        .join(Course, Question.course_id == Course.id)
        .filter(Attempt.user_id == user_id)
        .order_by(Attempt.created_at.desc())
        .all()
    )

    # group by course
    courses = {}
    for attempt, question, course in rows:
        c = courses.setdefault(course.id, {
            "course_id": course.id, "course_name": course.name,
            "attempts": [], "total_awarded": 0, "total_available": 0,
        })
        fb = json.loads(attempt.feedback_json) if attempt.feedback_json else {}
        c["attempts"].append({
            "attempt_id": attempt.id,
            "year": question.year, "paper": question.paper,
            "question_number": question.question_number,
            "part_label": fb.get("part_label", ""),
            "marks_awarded": fb.get("marks_awarded", attempt.awarded_mark),
            "marks_available": fb.get("marks_available"),
            "gaps": fb.get("gaps", ""),
            "feedback": fb.get("feedback", ""),
        })
        c["total_awarded"] += fb.get("marks_awarded", 0) or 0
        c["total_available"] += fb.get("marks_available", 0) or 0

    # for each course, get or regenerate the improvement summary
    for cid, c in courses.items():
        n = len(c["attempts"])
        cached = s.query(ImprovementSummary).filter_by(user_id=user_id, course_id=cid).first()
        if cached and cached.attempt_count == n:
            c["improvement_summary"] = cached.summary_text          # reuse cache
        else:
            feedback_items = [
                f"Q{a['year']} P{a['paper']}Q{a['question_number']} ({a['part_label']}): "
                f"gaps: {a['gaps']} | feedback: {a['feedback']}"
                for a in c["attempts"] if a["gaps"] or a["feedback"]
            ]
            summary = generate_summary(c["course_name"], feedback_items) if feedback_items else "Keep practising to build up feedback."
            if cached:
                cached.summary_text = summary
                cached.attempt_count = n
            else:
                s.add(ImprovementSummary(user_id=user_id, course_id=cid,
                                         summary_text=summary, attempt_count=n))
            s.commit()
            c["improvement_summary"] = summary

    s.close()
    return {"courses": list(courses.values())}