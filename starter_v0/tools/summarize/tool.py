from __future__ import annotations

import re
from typing import Any

from tools._shared import err


def summarize_text(text: str = "", max_sentences: int = 3) -> dict[str, Any]:
    try:
        if not text:
            return {"tool": "summarize", "summary": "", "sentence_count": 0}

        pieces = re.split(r'(?<=[.!?])\s+', text.strip())
        pieces = [part.strip() for part in pieces if part.strip()]
        summary = " ".join(pieces[: max(1, min(max_sentences, len(pieces)))])
        if len(pieces) > max_sentences:
            summary = summary.rstrip(".?!") + "..."
        return {
            "tool": "summarize",
            "text": text,
            "summary": summary,
            "sentence_count": len(pieces),
            "used_sentences": min(len(pieces), max_sentences),
        }
    except Exception as exc:
        return err("summarize", exc)
