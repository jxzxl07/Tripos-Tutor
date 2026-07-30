from datetime import datetime
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True)

    questions: Mapped[list["Question"]] = relationship(back_populates="course")


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    year: Mapped[int] = mapped_column(Integer)
    paper: Mapped[int] = mapped_column(Integer)
    question_number: Mapped[int] = mapped_column(Integer)
    question_text: Mapped[str] = mapped_column(Text)
    source_pdf_path: Mapped[str] = mapped_column(String(500))
    context_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    course: Mapped["Course"] = relationship(back_populates="questions")
    mark_scheme: Mapped["MarkScheme | None"] = relationship(
        back_populates="question", uselist=False
    )


class MarkScheme(Base):
    __tablename__ = "mark_schemes"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), unique=True)
    scheme_text: Mapped[str] = mapped_column(Text)
    source_pdf_path: Mapped[str] = mapped_column(String(500))

    question: Mapped["Question"] = relationship(back_populates="mark_scheme")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    google_sub: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Attempt(Base):
    __tablename__ = "attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_text: Mapped[str] = mapped_column(Text)
    awarded_mark: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Rubric(Base):
    __tablename__ = "rubrics"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), unique=True)
    total_marks: Mapped[int] = mapped_column(Integer)
    criteria_json: Mapped[str] = mapped_column(Text)   # JSON: list of {point, marks}
    grounded_in_scheme: Mapped[bool] = mapped_column(default=False)

    question: Mapped["Question"] = relationship()


class QuestionPart(Base):
    __tablename__ = "question_parts"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    label: Mapped[str] = mapped_column(String(10))       # "a", "b", "c"...
    order_index: Mapped[int] = mapped_column(Integer)    # 0, 1, 2... for ordering
    part_text: Mapped[str] = mapped_column(Text)
    marks: Mapped[int | None] = mapped_column(Integer, nullable=True)

    question: Mapped["Question"] = relationship()

class ImprovementSummary(Base):
    __tablename__ = "improvement_summaries"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    summary_text: Mapped[str] = mapped_column(Text)
    attempt_count: Mapped[int] = mapped_column(Integer)