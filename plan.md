# Tripos Tutor — AI Revision Platform: Overall Plan & Feature List

A full-stack AI revision platform for Cambridge CS students. Ingests 20+ years of
Part IB past papers, marks free-text answers against real mark schemes, teaches the
topics that matter, and shows each user exactly where they're weak.

**Guiding principle:** ship a complete, deployable loop your coursemates actually use
before exams. Real usage beats extra features. Tags below:
**[v1]** = build now (core, deployable). **[v2]** = roadmap (design now, build live after launch).

---

## 1. Feature List

### A. Accounts & user data
- **Google OAuth login**, restricted to `cam.ac.uk` — no passwords, auto-gates to real Cambridge students. **[v1]**
- **Per-user accounts** with persistent state: attempts, marks, feedback, weakness profile, progress. **[v1]**
- **Per-user uploaded materials** — own notes/papers ingested into a private, isolated space (never a shared central corpus). **[v2]**

### B. Practice & marking (the core loop)
- **Past-paper question bank** — browse/filter by course, topic, and year. **[v1]**
- **Answer submission** — free-text box per question. **[v1]**
- **AI answer marking** against the real mark scheme: awarded mark + structured feedback (criteria hit/missed, how to improve). *Headline feature.* **[v1]**
- **Mark-scheme breakdown** shown beside the mark, so feedback is transparent and learnable. **[v1]**
- **Grounding / citations** — marks and answers cite the source (which paper, mark scheme, or note). **[v1]**
- **Streaming feedback** (SSE) — feedback appears token-by-token, feels fast. **[v1]**
- **Question variations** — "give me another like this" to drill a weak concept with fresh questions. **[v1]**
- **Model-answer comparison** — user's answer side by side with a strong answer, differences highlighted. **[v2]**
- **Exam mode** — timed full past paper, then batch-marked with per-question feedback and a total. **[v2]**

### C. Analysis & diagnosis
- **Topic-frequency analysis** per course — which topics recur, how often, trends over ~20 years. **[v1]**
- **Predictability score** per course — how stable each course's topic distribution is (describe patterns honestly; don't over-claim prediction). **[v1]**
- **Weakness dashboard** — per-user performance broken down by topic. **[v1]**
- **Weakness × frequency priority ranking** — "revise concurrency first: you score 40% and it appears in 19/20 papers." *The feature nothing else can replicate; centre of the dashboard.* **[v1]**
- **Progress-over-time** — improvement trends, not just current state (the retention hook). **[v1 if schema allows, else v2]**
- **Syllabus-diff checker** — flag past questions testing material no longer on the current syllabus. **[v2]**

### D. Teaching
- **Teaching mode per course** — teach exactly what's needed for high marks, over the user's own notes, focused by frequency + weakness data (teach → practice → mark loop). **[v2]**
- **"Teach me this topic"** — grounded explanation built from the user's real course notes (matches their lecturer's notation), flowing straight from the weakness ranking. **[v2]**
- **Tutor chat** — scoped per question: progressive hints ("explain like I'm stuck"), then method, then worked solution. Protects learning; not a cheat button. **[v2]**
- **Revision timetable / "what do I study today"** — from weakness × frequency + exam dates. **[v2]**

### E. Community & motivation
- **Shared question bank / topic threads** — coursemates flag hard questions, add notes/better explanations. Drives word-of-mouth adoption. **[v2]**
- **Leaderboard / streaks** — opt-in, gentle ("30 questions marked this week"). Retention. **[v2]**
- **Landing page** — 10-second explanation so coursemates find and understand it. **[v1]**

---

## 2. Engineering layers (what makes it a flagship, not a wrapper)

### AI engineering
- **Hand-rolled RAG pipeline** — chunk → embed (Gemini embeddings) → store in pgvector → retrieve by similarity → assemble context. No LangChain; you understand and can explain every step. **[v1]**
- **Dual-corpus grounding** — retrieval over both past papers and (v2) the user's notes, with citations. **[v1 papers / v2 notes]**
- **Structured LLM outputs** — Gemini returns JSON to a Pydantic schema for marking (reliable, parseable). **[v1]**
- **Model routing** — Gemini Flash for cheap/high-volume tasks (variations, hints), Pro for marking where quality matters. **[v1]**
- **Response & embedding caching** — don't re-mark identical answers; don't re-embed unchanged text. **[v1]**
- **Eval harness (pytest)** — run the marker over a labelled set of answers with known marks; report marking accuracy/correlation. *Clearest possible "I do AI engineering" signal — un-cuttable.* **[v1]**
- **Prompt templates** kept versioned and centralised. **[v1]**

### Data engineering
- **PDF ingestion pipeline** — PyMuPDF parses papers into structured questions; links each to its mark scheme by paper/year/number. *Feature zero — everything depends on it.* **[v1]**
- **Notes ingestion** — chunking + notation handling for terse, diagram-heavy slides (a real sub-task, not a freebie). **[v2]**
- **Topic tagging** — LLM-assisted tagging of questions to topics (sample-verified). **[v1]**
- **Frequency aggregation + predictability metric** computed from tagged questions. **[v1]**

### Platform / non-functional
- **Auth & session management** (OAuth flow, JWT/sessions). **[v1]**
- **Per-user rate limiting.** **[v1]**
- **LLM cost control** — caching + routing + token budgeting. **[v1]**
- **Observability** — structured request logging, tracing, a small admin usage dashboard. **[v1]**
- **Secrets management** — no keys in the repo, ever (env locally, Key Vault / Container Apps secrets in prod). **[v1]**
- **Migrations** — Alembic for versioned schema. **[v1]**
- **CI/CD** — GitHub Actions: test → build → deploy. **[v1]**
- **Containerised single-service deploy** — React built to static files, served by FastAPI in one container. **[v1]**
- **Graceful degradation & error handling** around LLM/API failures. **[v1]**

---

## 3. Tech Stack (final)

| Layer | Choice |
|---|---|
| Backend | Python + FastAPI (async) |
| Frontend | React + Vite (plain JS), Tailwind, Recharts |
| Database | PostgreSQL + pgvector |
| ORM / driver / migrations | SQLAlchemy (async) + asyncpg + Alembic |
| LLM | Google Gemini (Flash + Pro) + Gemini embeddings |
| PDF parsing | PyMuPDF |
| Auth | Google OAuth, cam.ac.uk-restricted |
| Container / hosting | Docker → Azure Container Apps + Azure DB for PostgreSQL |
| Storage | Azure Blob Storage (uploads) |
| CI/CD | GitHub Actions |
| Secrets | Key Vault / Container Apps secrets |
| Tests / evals | pytest |

**Deploy gotcha:** FastAPI is a running server; a built React app is static files.
For a solo build, **serve the React build from FastAPI in one container** —
one URL, one pipeline, no CORS. Split to Azure Static Web Apps only if you later
need independent scaling (you won't, at cohort scale).

---

## 4. Architecture (monorepo, thin routers over testable services)

```
tripos-tutor/
├── backend/app/
│   ├── main.py            # FastAPI entry; routers + static React build
│   ├── config.py / db.py
│   ├── models/           # users, courses, papers, questions, mark_schemes,
│   │                     #   topics, question_topics, attempts, embeddings
│   ├── schemas/          # Pydantic request/response + LLM structured-output schemas
│   ├── auth/             # Google OAuth, sessions
│   ├── routers/          # papers, marking, dashboard, analysis, variations
│   ├── services/         # ingestion, rag, marking, analysis, llm
│   └── evals/            # pytest eval harness
│   ├── migrations/  tests/  Dockerfile  pyproject.toml
├── frontend/src/         # pages/ components/ api/  (Vite)
├── .github/workflows/    docker-compose.yml    .gitignore    README.md
```

**Data model (core tables):** users, courses, papers, questions, mark_schemes,
topics, question_topics, attempts, embeddings.
Key point: **marking is a structured lookup** (question → its mark scheme by ID),
**not** fuzzy RAG. Vector retrieval powers the notes-based flows (variations, teaching).

---

## 5. Feature dependencies (build order, not a schedule)

```
ingestion  ──►  everything (papers must be parsed & stored first)
   ├─ auth/accounts  ──►  all per-user data attaches here
   ├─ MARKING (headline)  ──►  attempts saved  ──►  weakness dashboard
   ├─ topic tagging  ──►  frequency + predictability  ──►  priority ranking (weakness × frequency)
   └─ RAG pipeline  ──►  question variations  ──►  (v2) teaching mode, tutor chat
```

---

## 6. Scope discipline — if you run short

Cut in this order (protect the core loop): predictability score → question variations →
fancy visuals (a ranked list still delivers) → **React fallback to plain HTML/CSS/JS**
(a shipped plain-JS app beats a broken React one).
**Never cut:** ingestion, marking, auth, the eval harness, the deploy.

---

## 7. Honesty / risk notes

- **Copyright:** past papers + mark schemes are university-published (safe to host). Lecture **notes** are lecturers' copyright — keep them **per-user, isolated uploads**, never one shared corpus. Cleaner engineering too.
- **Ingestion quality** is real work (terse, notation-heavy sources embed badly) — and a good CV talking point.
- **Usage numbers must be real** — only put "used by N students / N answers marked" on the CV once true; otherwise use capability framing.
- **Only claim the paper range you actually ingest.**

---

## 8. Success criteria

1. A live URL a recruiter can click and use.
2. Full loop works: question → answer → accurate mark + feedback → saved → reflected in the dashboard.
3. Eval harness reporting a real marking-accuracy figure.
4. Real coursemates using it, with a citable usage number.
5. A README strong enough that an engineer understands the architecture without running it.
