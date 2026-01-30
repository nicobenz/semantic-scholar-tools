from fastapi import FastAPI
from app.service.search import (
    get_client,
    get_papers,
    get_paper_details,
    get_citations_and_references,
)

app = FastAPI(
    title="Semantic Scholar LLM Tool Server",
    description="Tool server for accessing data from Semantic Scholar for LLMs",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

USER_AGENT = "semantic-scholar-llm-tool-server/0.0.1"

client = get_client()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing API information"""
    return {
        "name": "Semantic Scholar Tools API",
        "version": "0.1.0",
        "description": "API for accessing the API of Semantic Scholar",
        "endpoints": {
            "search": "/api/search",
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


@app.get("/api/search", tags=["Search"], response_model=dict)
async def query_papers(query: str, limit: int = 10):
    """Search semantic scholar. Pass your search query via the `query` query parameter."""
    return get_papers(client=client, query=query, count=limit)


@app.get("/api/details", tags=["Paper Details"], response_model=dict)
async def query_paper_details():
    """Search semantic scholar"""
    return get_paper_details()


@app.get("/api/references", tags=["References"], response_model=dict)
async def query_paper_references():
    """Search semantic scholar"""
    return get_citations_and_references()


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
