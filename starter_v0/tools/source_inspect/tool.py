from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def _meta_tag(html: str, names: list[str]) -> str:
    for name in names:
        pattern = rf'<meta[^>]+(?:name|property)=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']'
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _clean_snippet(text: str, length: int = 300) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    return clean[:length] + "..." if len(clean) > length else clean


def source_inspect(url: str = "") -> dict[str, Any]:
    try:
        if not url or not url.strip():
            raise ValueError("Missing url for source inspection")

        response = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "AI20k-SourceInspect/1.0"})
        response.raise_for_status()
        html = response.text

        title = _meta_tag(html, ["og:title", "twitter:title", "title"])
        if not title:
            title_match = re.search(r"<title>([^<]+)</title>", html, flags=re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ""

        description = _meta_tag(html, ["og:description", "twitter:description", "description"])
        canonical = _meta_tag(html, ["og:url", "canonical"])
        https = url.lower().startswith("https://")
        snippet = _clean_snippet(re.sub(r"<[^>]+>", " ", html), 250)

        return {
            "tool": "source_inspect",
            "url": url,
            "domain": domain(url),
            "https": https,
            "status_code": response.status_code,
            "title": title,
            "description": description,
            "canonical_url": canonical or url,
            "content_snippet": snippet,
        }
    except Exception as exc:
        return err("source_inspect", exc)
