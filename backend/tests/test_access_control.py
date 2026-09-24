"""End-to-end check of the IDOR fix on an in-memory SQLite DB with a fake LLM:
each user can only create and read their OWN attempts."""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import Course, Question, QuestionPart, User
from app.models.base import Base
from app.routers import dashboard as dashboard_router
from app.security import create_access_token
from app.services import marking
from app.services.marking import PartMarkingResult


@pytest.fixture()
def env(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    s = Session()
    alice = User(google_sub="a", email="alice@cam.ac.uk", name="Alice")
    bob = User(google_sub="b", email="bob@cam.ac.uk", name="Bob")
    course = Course(name="Compiler Construction", slug="Compiler-Construction")
    s.add_all([alice, bob, course]); s.flush()
    q = Question(course_id=course.id, year=2024, paper=4, question_number=3,
                 question_text="...", source_pdf_path="x.pdf")
    s.add(q); s.flush()
    part = QuestionPart(question_id=q.id, label="a", order_index=0, part_text="Define X.", marks=4)
    s.add(part); s.commit()
    ids = SimpleNamespace(alice=alice.id, bob=bob.id, part=part.id)
    s.close()

    def _get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    fake_result = PartMarkingResult(marks_awarded=3, marks_available=4,
                                    strengths="s", gaps="g", feedback="f")
    monkeypatch.setattr(marking, "client", SimpleNamespace(models=SimpleNamespace(
        generate_content=lambda **kw: SimpleNamespace(parsed=fake_result))))
    monkeypatch.setattr(dashboard_router, "client", SimpleNamespace(models=SimpleNamespace(
        generate_content=lambda **kw: SimpleNamespace(text="revise X"))))

    app.dependency_overrides[get_db] = _get_db
    yield TestClient(app), ids
    app.dependency_overrides.clear()


def _auth(user_id):
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


def test_users_only_see_their_own_attempts(env):
    client, ids = env
    r = client.post("/api/mark", json={"part_id": ids.part, "answer": "Alice's answer"},
                    headers=_auth(ids.alice))
    assert r.status_code == 200 and r.json()["marks_awarded"] == 3

    alice_dash = client.get("/api/dashboard/me", headers=_auth(ids.alice)).json()
    bob_dash = client.get("/api/dashboard/me", headers=_auth(ids.bob)).json()
    assert len(alice_dash["courses"][0]["attempts"]) == 1
    assert bob_dash["courses"] == []            # Bob cannot see Alice's attempt


def test_attempt_is_saved_under_token_user_not_body(env):
    client, ids = env
    # An attacker adds user_id to the body; it must be ignored.
    client.post("/api/mark", json={"part_id": ids.part, "answer": "x", "user_id": ids.alice},
                headers=_auth(ids.bob))
    alice_dash = client.get("/api/dashboard/me", headers=_auth(ids.alice)).json()
    bob_dash = client.get("/api/dashboard/me", headers=_auth(ids.bob)).json()
    assert alice_dash["courses"] == []
    assert len(bob_dash["courses"][0]["attempts"]) == 1


def test_token_for_deleted_user_rejected(env):
    client, _ = env
    r = client.get("/api/dashboard/me", headers=_auth(999))
    assert r.status_code == 401
