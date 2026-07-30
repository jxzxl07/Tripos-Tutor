"""Pytest eval: asserts the marker achieves acceptable accuracy on labelled cases."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.evals.run_evals import run

def test_marking_accuracy():
    results, passed, n = run()
    assert n > 0, "No eval cases ran"
    accuracy = passed / n
    # Require at least 70% of cases within their expected mark range
    assert accuracy >= 0.7, f"Marking accuracy {accuracy:.0%} below 70% threshold"