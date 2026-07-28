from fastapi import FastAPI

app = FastAPI(title="Tripos Tutor")

@app.get("/api/health")
def health():
    return {"status": "ok"}