"""Offline test setup: dummy settings so the app imports without real secrets.
No test here touches the network or a real database."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Live evals (RUN_LLM_EVALS=1) must read the real values from .env instead.
if os.environ.get("RUN_LLM_EVALS") != "1":
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    os.environ.setdefault("GEMINI_API_KEY", "test-key")
    os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
    os.environ.setdefault("SESSION_SECRET", "test-secret-" + "x" * 40)
