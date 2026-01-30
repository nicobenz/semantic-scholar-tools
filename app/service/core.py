"""CORE API v3 client for searching works (papers)."""

import asyncio
from typing import Any

import httpx

CORE_SEARCH_URL = "https://api.core.ac.uk/v3/search/works/"

# CORE's Elasticsearch sometimes returns "rejected execution" when overloaded; retry once.
CORE_RETRY_DELAY = 2.0


def _is_core_overloaded(response_text: str) -> bool:
    """True if CORE returned an overload/rejected-execution error."""
    return (
        "rejected execution" in response_text
        or "rejected_execution" in response_text
        or "es_rejected_execution" in response_text
    )


async def search_works(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search CORE for works (papers). Returns list of papers in a uniform shape."""
    params = {"q": query, "limit": min(limit, 100), "offset": 0}
    headers: dict[str, str] = {}
    last_error: httpx.HTTPStatusError | None = None

    for attempt in range(2):
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(CORE_SEARCH_URL, params=params, headers=headers)
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                last_error = e
                retryable = attempt == 0 and (
                    resp.status_code >= 500 or _is_core_overloaded(resp.text)
                )
                if retryable:
                    await asyncio.sleep(CORE_RETRY_DELAY)
                    continue
                raise
            data = resp.json()
            results = data.get("results") or []
            return [_work_to_paper(w) for w in results]

    if last_error:
        raise last_error
    return []


def _work_to_paper(work: dict[str, Any]) -> dict[str, Any]:
    """Map CORE work to our paper shape (id, title, abstract, year, authors, url, venue, type)."""
    authors_raw = work.get("authors") or []
    authors = [
        {"name": a.get("name", a) if isinstance(a, dict) else str(a), "id": None}
        for a in authors_raw
    ]

    links = work.get("links") or []
    url = None
    for link in links:
        if isinstance(link, dict) and link.get("url"):
            url = link["url"]
            break
    if not url and work.get("downloadUrl"):
        url = work["downloadUrl"]

    doc_type = work.get("documentType")
    if isinstance(doc_type, list):
        doc_type = doc_type[0] if doc_type else None

    journals = work.get("journals") or []
    venue = work.get("publisher") or (journals[0].get("title") if journals else None)

    return {
        "id": str(work.get("id", "")),
        "title": work.get("title") or "",
        "abstract": work.get("abstract") or "",
        "year": work.get("yearPublished"),
        "authors": authors,
        "url": url,
        "venue": venue,
        "type": doc_type,
        "citations": work.get("citationCount"),
    }
