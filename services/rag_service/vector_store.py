from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

from .embeddings import generate_embedding


VECTOR_DB_PATH = "rag_data/vector_db"
COLLECTION_NAME = "insurance_documents"

client = QdrantClient(
    path=VECTOR_DB_PATH
)


def initialize_collection():
    if client.collection_exists(COLLECTION_NAME):
        return

    sample_vector = generate_embedding(
        "insurance document"
    )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=len(sample_vector),
            distance=Distance.COSINE
        )
    )


def add_document(
    document_id: int,
    text: str,
    metadata: dict
):
    vector = generate_embedding(text)

    point = PointStruct(
        id=document_id,
        vector=vector,
        payload={
            "text": text,
            **metadata
        }
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )


def search_documents(
    query: str,
    limit: int = 3
):
    query_vector = generate_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit
    ).points

    return [
        {
            "score": result.score,
            **result.payload
        }
        for result in results
    ]