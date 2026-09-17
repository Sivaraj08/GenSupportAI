from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .config import settings
from .database import engine, Base, get_db
from .routers import document, chat, ticket, analytics
from .services.rag_service import rag_service

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(document.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(ticket.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "features": ["RAG Ingestion Engine"]
    }

@app.get("/api/documents/search")
def search_documents(query: str, limit: int = 3):
    """
    Utility endpoint to test vector similarity searches.
    Enables manual testing of the RAG indexing system.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query string parameter is required.")
    
    try:
        matches = rag_service.query_similarity(query, top_k=limit)
        return {"query": query, "results": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity query failed: {str(e)}")
