from fastapi import FastAPI
from app.routers import questions, marking, auth, dashboard

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
app.include_router(dashboard.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Serve the built React frontend (in production)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend_dist")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # serve index.html for any non-API route (React handles routing client-side)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))