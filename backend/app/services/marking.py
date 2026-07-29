"""
Marks a student's free-text answer against a question's stored rubric.
Returns a structured result: overall mark, what scored, what was missed, and why.
"""
import json
from pydantic import BaseModel
from app.services.llm import client, PRO


class CriterionResult(BaseModel):
    point: str              # the rubric point being assessed
    marks_available: int
    marks_awarded: int
    comment: str            # why they got / didn't get these marks

class MarkingResult(BaseModel):
    total_awarded: int
    total_available: int
    strengths: str          # what the answer did well (what scored)
    gaps: str               # what was missing or wrong (what was missed)
    overall_feedback: str   # summary + how to improve


MARKING_PROMPT = """You are a Cambridge Computer Science Tripos examiner marking a
student's answer against the marking rubric. Be fair but rigorous — award marks only
for points the student genuinely addresses. For each rubric criterion, decide how many
of its marks the answer earns and why. Then summarise strengths, gaps, and overall
feedback with concrete advice.

QUESTION:
{question}

MARKING RUBRIC (criteria and marks):
{rubric}

STUDENT'S ANSWER:
{answer}
"""


def mark_answer(question_text: str, rubric_criteria: list[dict], total_marks: int,
                student_answer: str) -> MarkingResult:
    rubric_str = "\n".join(
        f"- [{c['marks']} marks] {c['point']}" for c in rubric_criteria
    )
    prompt = MARKING_PROMPT.format(
        question=question_text,
        rubric=f"Total: {total_marks} marks\n{rubric_str}",
        answer=student_answer,
    )
    resp = client.models.generate_content(
        model=PRO,                      # Pro for marking — quality matters here
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": MarkingResult,
            "http_options": {"timeout": 60000},
        },
    )
    return resp.parsed