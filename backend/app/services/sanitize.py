"""Treat student answers as untrusted input before they reach the LLM prompt."""
import re

MAX_ANSWER_CHARS = 5000

# ASCII control chars (keep \t \n \r), DEL, and invisible Unicode that can hide
# text from a human reviewer: zero-width chars, bidi overrides/isolates, BOM.
_INVISIBLE = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f"
    r"\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]"
)

# Any open/close form of our delimiter tag, so an answer can't close the
# <student_answer> block early and smuggle instructions after it.
_DELIMITER = re.compile(r"<\s*/?\s*student_answer\s*>", re.IGNORECASE)


def clean_answer(text: str) -> str:
    text = _INVISIBLE.sub("", text)
    text = _DELIMITER.sub("[removed tag]", text)
    return text.strip()
