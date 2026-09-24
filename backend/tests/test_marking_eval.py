"""Pytest eval: asserts the marker achieves acceptable accuracy on labelled cases.

Calls the live Gemini API and needs a seeded database, so it only runs when
RUN_LLM_EVALS=1 is set (locally). CI runs the offline tests only.
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_LLM_EVALS") != "1",
    reason="live LLM eval; set RUN_LLM_EVALS=1 to run",
)


def test_marking_accuracy():
    from app.evals.run_evals import run
    results, passed, n = run()
    assert n > 0, "No eval cases ran"
    accuracy = passed / n
    # Require at least 70% of cases within their expected mark range
    assert accuracy >= 0.7, f"Marking accuracy {accuracy:.0%} below 70% threshold"
