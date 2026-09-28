from .vector_store import search_documents


def semantic_search(
    query: str,
    limit: int = 3
):
    return search_documents(
        query=query,
        limit=limit
    )