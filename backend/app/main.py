from fastapi import FastAPI
from app.routers import questions, marking, auth

app = FastAPI(title="Tripos Tutor")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(marking.router)
app.include_router(auth.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}