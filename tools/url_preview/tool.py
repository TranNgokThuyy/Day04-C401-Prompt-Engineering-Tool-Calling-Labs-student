from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import err, domain


def _first_match(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.I | re.S)
    return match.group(1).strip() if match else ""


def preview_url(url: str = "") -> dict[str, Any]:
    try:
        if not url:
            raise ValueError("Missing url")
        response = requests.get(url, timeout=15, headers={"User-Agent": "ResearchAgent/1.0"})
        response.raise_for_status()
        html = response.text
        title = _first_match(html, r"<title>(.*?)</title>")
        description = _first_match(html, r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']')
        if not description:
            description = _first_match(html, r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']')
        return {
            "tool": "url_preview",
            "url": url,
            "domain": domain(url),
            "status_code": response.status_code,
            "title": title,
            "description": description,
        }
    except Exception as exc:
        return err("url_preview", exc)
