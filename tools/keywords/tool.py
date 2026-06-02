from __future__ import annotations

from typing import Any

from tools._shared import err, terms


def extract_keywords(text: str = "", max_keywords: int = 8) -> dict[str, Any]:
    try:
        if not text:
            return {"tool": "keywords", "keywords": []}
        extracted = sorted(terms(text), key=lambda token: (-text.lower().count(token), len(token)))
        unique = []
        for token in extracted:
            if token not in unique:
                unique.append(token)
            if len(unique) >= max_keywords:
                break
        return {"tool": "keywords", "text": text, "keywords": unique}
    except Exception as exc:
        return err("keywords", exc)
