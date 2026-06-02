from __future__ import annotations

from collections import Counter
from typing import Any

from tools._shared import err, terms


def trend_analysis(texts: list[str] | None = None, focus_topic: str = "", top_k: int = 5) -> dict[str, Any]:
    try:
        texts = texts or []
        if not texts:
            raise ValueError("Missing texts for trend analysis")

        top_k = max(1, min(int(top_k or 5), 10))
        focus_topic = (focus_topic or "").strip()

        all_terms = Counter()
        for text in texts:
            all_terms.update(terms(text))

        top_topics = [term for term, _ in all_terms.most_common(top_k)]
        if focus_topic:
            top_topics.insert(0, focus_topic)
            top_topics = list(dict.fromkeys(top_topics))[:top_k]

        summary = (
            f"Xu hướng chính: {', '.join(top_topics)}."
            if top_topics
            else "Không đủ dữ liệu để xác định xu hướng."
        )

        return {
            "tool": "trend_analysis",
            "texts": texts,
            "focus_topic": focus_topic,
            "top_k": top_k,
            "top_topics": top_topics,
            "summary": summary,
            "item_count": len(texts),
        }
    except Exception as exc:
        return err("trend_analysis", exc)
