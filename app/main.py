import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request
from tenacity import RetryError

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

client = get_client()


def _is_semantic_scholar_429(exc: BaseException) -> bool:
    if isinstance(exc, ConnectionRefusedError) and exc.args:
        return "429" in str(exc.args[0])
    if isinstance(exc, RetryError):
        # tenacity sets __cause__ to the underlying exception
        cause = getattr(exc, "__cause__", None) or getattr(exc, "__context__", None)
        if cause is not None and _is_semantic_scholar_429(cause):
            return True
        # fallback: check message in case cause chain is missing
        if "429" in str(exc) or "Too Many Requests" in str(exc):
            return True
    return False


@app.exception_handler(ConnectionRefusedError)
@app.exception_handler(RetryError)
async def semantic_scholar_rate_limit(
    request: Request, exc: BaseException
) -> JSONResponse:
    if _is_semantic_scholar_429(exc):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Semantic Scholar rate limit exceeded. Use an API key for higher limits.",
            },
        )
    raise exc


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
    return await asyncio.to_thread(get_papers, client=client, query=query, count=limit)


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
