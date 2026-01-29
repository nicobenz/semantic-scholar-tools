from fastapi import FastAPI
from app.service.search import (
    get_papers,
    get_paper_details,
    get_citations_and_references,
)

app = FastAPI(
    title="Teaching Tools API",
    description="API for accessing curriculum sections for various subjects",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

USER_AGENT = "semantic-scholar-llm-tool-server/0.0.1"


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
async def query_papers():
    """Search semantic scholar"""
    return get_papers()


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
