from __future__ import annotations

import re
from typing import Any

from tools._shared import err

POSITIVE_TERMS = {
    "tốt", "tuyệt", "xuất sắc", "tích cực", "khả quan", "thành công", "mạnh", "đỉnh", "cơ hội",
    "hữu ích", "đột phá", "thăng hoa", "đáng khen", "lợi", "thích", "yêu",
}
NEGATIVE_TERMS = {
    "xấu", "tiêu cực", "kém", "thất bại", "lo lắng", "bất lợi", "rủi ro", "mờ", "suy giảm",
    "khó", "tệ", "đau", "bất ổn", "phàn nàn", "bức xúc", "nghi ngờ",
}


def _normalize_terms(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZÀ-Ỹà-ỹ0-9]+", text.lower())


def sentiment(text: str = "") -> dict[str, Any]:
    try:
        if not text or not text.strip():
            raise ValueError("Missing text for sentiment analysis")

        tokens = _normalize_terms(text)
        positive = [token for token in tokens if token in POSITIVE_TERMS]
        negative = [token for token in tokens if token in NEGATIVE_TERMS]
        metric = 0
        if positive or negative:
            metric = (len(positive) - len(negative)) / max(1, len(positive) + len(negative))

        if metric >= 0.2:
            sentiment_label = "positive"
        elif metric <= -0.2:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        summary = (
            "Dạng tích cực" if sentiment_label == "positive"
            else "Dạng tiêu cực" if sentiment_label == "negative"
            else "Dạng trung tính"
        )

        return {
            "tool": "sentiment",
            "text": text,
            "sentiment": sentiment_label,
            "score": round(metric, 3),
            "positive_terms": positive,
            "negative_terms": negative,
            "summary": summary,
        }
    except Exception as exc:
        return err("sentiment", exc)
