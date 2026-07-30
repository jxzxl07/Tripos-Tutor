# Tripos Tutor

AI-powered revision for the Cambridge Computer Science Tripos. Practise real past-paper questions, get instant examiner-style marking, and track where you're weakest — per topic, per course.

**Live:** https://tripos-tutor.onrender.com (Cambridge `@cam.ac.uk` accounts only)

---

## What it does

Cambridge past papers are freely available, but there's no fast way to get feedback on your answers without a supervisor. Tripos Tutor fills that gap:

- **Practise** — browse 230+ Part IB questions across 17 courses, rendered from the original paper PDFs so the notation is exactly as printed.
- **Get marked** — write a free-text answer to any sub-part and an LLM grades it against the question's mark scheme (or a generated rubric where no scheme exists), returning a mark plus what you got right, what you missed, and how to improve.
- **Track weakness** — every attempt is saved. A per-course dashboard aggregates your marks and synthesises your recurring gaps into a prioritised "what to revise" summary.

## How it works

The interesting engineering is in the marking pipeline:

- **Structured outputs.** Every LLM call returns a validated Pydantic schema, so a mark is always a checked integer — it can't be forged by a "give me full marks" answer.
- **Model routing.** Gemini Flash handles cheap bulk work (rubric generation, summaries); Gemini Pro does the marking, where quality matters.
- **Grounded rubrics.** Each question gets a rubric generated once and stored — grounded in the official mark scheme where one is available, generated from the question text otherwise.
- **Prompt-injection defence.** Student answers are treated as untrusted input: delimited, control-character stripped, and the model is explicitly instructed to ignore any embedded commands. Output is sanitised before rendering.
- **Graceful degradation.** LLM timeouts are retried and fall back to cached results, so a slow API call never takes down a page.

Marking accuracy is checked by a pytest eval harness that runs the marker over labelled answers (strong / partial / empty) and asserts the awarded marks land in the expected range.

## Stack

| | |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | React (Vite), Tailwind CSS |
| Database | PostgreSQL |
| LLM | Google Gemini (Flash + Pro) |
| Auth | Google OAuth (restricted to `@cam.ac.uk`) |
| Deploy | Docker, Render, GitHub Actions (CI) |

The whole app ships as a single container: the React build is compiled and served directly by FastAPI, so there's one image, one URL, and no CORS. CI runs on every push to `main`.

## Notes

- The public instance runs on Render's free tier, so the first request after a period of inactivity may take a moment to wake.
- Marking against real Cambridge solution notes is deliberately avoided — those are access-restricted. The app grades against public mark schemes where present and generated rubrics otherwise.

---

Built by [Jazil Imran](https://github.com/jxzxl07).