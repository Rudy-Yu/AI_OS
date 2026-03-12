"""
Web search tool for AI_OS.

Uses DuckDuckGo Instant Answer API (no API key required).
"""

from __future__ import annotations

from typing import Any, Dict, List

import requests

from core.logger import get_logger

logger = get_logger(__name__)


def search(query: str) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo Instant Answer API.

    Args:
        query: Search query string.

    Returns:
        List of results (best-effort normalized).
    """
    try:
        url = "https://api.duckduckgo.com/"
        resp = requests.get(url, params={"q": query, "format": "json"}, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        results: List[Dict[str, Any]] = []

        if data.get("AbstractText"):
            results.append(
                {
                    "title": data.get("Heading") or "Abstract",
                    "snippet": data.get("AbstractText"),
                    "url": data.get("AbstractURL") or "",
                }
            )

        for item in data.get("RelatedTopics", []) or []:
            # RelatedTopics can be nested.
            if isinstance(item, dict) and "Topics" in item:
                for sub in item.get("Topics") or []:
                    if isinstance(sub, dict) and sub.get("Text"):
                        results.append(
                            {
                                "title": (sub.get("Text") or "").split(" - ")[0][:120],
                                "snippet": sub.get("Text") or "",
                                "url": sub.get("FirstURL") or "",
                            }
                        )
            elif isinstance(item, dict) and item.get("Text"):
                results.append(
                    {
                        "title": (item.get("Text") or "").split(" - ")[0][:120],
                        "snippet": item.get("Text") or "",
                        "url": item.get("FirstURL") or "",
                    }
                )

        logger.info(f"Web search done query={query!r} results={len(results)}")
        return results[:10]
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return []

