from semanticscholar import SemanticScholar, Paper
from typing import List, Dict, Any


def get_client():
    return SemanticScholar()


def get_papers(
    client: SemanticScholar, query: str, count: int = 10
) -> List[Dict[str, Any]]:
    """Search Semantic Scholar for papers via query."""
    search_results = client.search_paper(query, limit=count)
    return [
        {
            "id": paper.paperId,
            "title": paper.title,
            "abstract": paper.abstract,
            "year": paper.year,
            "authors": [
                {"name": author.name, "id": author.authorId} for author in paper.authors
            ],
            "url": paper.url,
            "venue": paper.venue,
            "type": paper.publicationTypes,
            "citations": paper.citationCount,
        }
        for paper in search_results
    ]


def get_paper_details(client: SemanticScholar, paper_id: str) -> Paper:
    """Get more details on specific paper."""
    return client.get_paper(paper_id)


def get_citations_and_references(paper: Paper) -> Dict[str, List[Dict[str, Any]]]:
    """Query references of the paper."""
    return {"citations": paper.citations, "references": paper.references}
