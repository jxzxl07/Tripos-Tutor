from fastapi import FastAPI
from app.routers import questions, marking

app = FastAPI(title="Tripos Tutor")

app.include_router(questions.router)
app.include_router(marking.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}