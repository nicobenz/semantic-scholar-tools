"""arXiv API client for searching papers. No API key required."""

from typing import Any

import arxiv


def search_papers(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search arXiv for papers. Returns list of papers in a uniform shape."""
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=min(limit, 100))
    results = list(client.results(search))
    return [_result_to_paper(r) for r in results]


def get_paper(arxiv_id: str) -> dict[str, Any] | None:
    """Get a single paper by arXiv ID (e.g. 2301.12345 or 2301.12345v1). Returns None if not found."""
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id.strip()])
    results = list(client.results(search))
    if not results:
        return None
    return _result_to_paper(results[0])


def _result_to_paper(result: arxiv.Result) -> dict[str, Any]:
    """Map arxiv.Result to our paper shape."""
    authors = [{"name": a.name, "id": None} for a in result.authors]
    year = result.published.year if result.published else None
    return {
        "id": result.get_short_id() if result.entry_id else "",
        "title": result.title or "",
        "abstract": result.summary or "",
        "year": year,
        "authors": authors,
        "url": result.entry_id or "",
        "venue": getattr(result, "journal_ref", None) or None,
        "type": "preprint",
        "citations": None,
    }
