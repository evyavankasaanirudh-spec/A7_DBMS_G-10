from fastapi import FastAPI
from pydantic import BaseModel

from .vector_store import (
    initialize_collection,
    add_document
)

from .semantic_search import semantic_search


app = FastAPI(
    title="Insurance RAG Microservice",
    description="Insurance Document Semantic Search using FastEmbed and Qdrant",
    version="1.0.0"
)


class DocumentRequest(BaseModel):
    document_id: int
    text: str
    document_type: str
    source: str


class SearchRequest(BaseModel):
    query: str
    limit: int = 3


@app.on_event("startup")
def startup_event():
    initialize_collection()


@app.get("/")
def root():
    return {
        "service": "RAG Service",
        "status": "running",
        "vector_database": "Qdrant",
        "embedding_model": "BAAI/bge-small-en-v1.5"
    }


@app.post("/documents")
def add_document_endpoint(
    request: DocumentRequest
):
    add_document(
        document_id=request.document_id,
        text=request.text,
        metadata={
            "document_type": request.document_type,
            "source": request.source
        }
    )

    return {
        "message": "Document added to vector database",
        "document_id": request.document_id
    }


@app.post("/search")
def search_endpoint(
    request: SearchRequest
):
    results = semantic_search(
        query=request.query,
        limit=request.limit
    )

    return {
        "query": request.query,
        "results": results
    }