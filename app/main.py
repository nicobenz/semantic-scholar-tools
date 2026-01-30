import asyncio
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.service import arxiv as arxiv_service


app = FastAPI(
    title="Paper Search API",
    description="Search papers and get paper details via arXiv",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# At most 1 arXiv request per second; requests wait for the next slot.
_search_last = [0.0]
_search_lock = asyncio.Lock()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing API information"""
    return {
        "name": "Paper Search API",
        "version": "0.1.0",
        "description": "Search papers via arXiv",
        "endpoints": {
            "search": "/api/search",
            "paper": "/api/paper/{arxiv_id}",
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


@app.get("/api/search", tags=["Papers"])
async def search_papers(query: str, limit: int = 10):
    """Get a few papers matching a query (e.g. natural language or keywords)."""
    async with _search_lock:
        wait = max(0.0, 1.0 - (time.monotonic() - _search_last[0]))
        if wait > 0:
            await asyncio.sleep(wait)
        result = await asyncio.to_thread(
            arxiv_service.search_papers, query=query, limit=limit
        )
        _search_last[0] = time.monotonic()
    return result


@app.get("/api/paper/{arxiv_id}", tags=["Papers"])
async def get_paper(arxiv_id: str):
    """Get full details of a single paper by its arXiv ID (e.g. 2301.12345)."""
    async with _search_lock:
        wait = max(0.0, 1.0 - (time.monotonic() - _search_last[0]))
        if wait > 0:
            await asyncio.sleep(wait)
        paper = await asyncio.to_thread(arxiv_service.get_paper, arxiv_id=arxiv_id)
        _search_last[0] = time.monotonic()
    if paper is None:
        return JSONResponse(
            status_code=404,
            content={"detail": f"No paper found for arXiv ID: {arxiv_id}"},
        )
    return paper


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
