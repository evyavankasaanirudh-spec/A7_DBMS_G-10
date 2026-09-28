from pathlib import Path

from .vector_store import initialize_collection, add_document


DOCUMENTS_DIR = Path("rag_data/policy_documents")


def ingest_documents():
    initialize_collection()

    documents = [
        {
            "id": 1,
            "file": "vehicle_claims.txt",
            "document_type": "Vehicle Insurance",
        },
        {
            "id": 2,
            "file": "health_claims.txt",
            "document_type": "Health Insurance",
        },
        {
            "id": 3,
            "file": "claim_processing.txt",
            "document_type": "Claim Processing",
        },
        {
            "id": 4,
            "file": "fraud_indicators.txt",
            "document_type": "Fraud Detection",
        },
    ]

    for document in documents:
        file_path = DOCUMENTS_DIR / document["file"]

        text = file_path.read_text(
            encoding="utf-8"
        )

        add_document(
            document_id=document["id"],
            text=text,
            metadata={
                "document_type": document["document_type"],
                "source": document["file"],
            }
        )

        print(
            f"Added: {document['file']}"
        )

    print("\nAll documents added to Qdrant.")


if __name__ == "__main__":
    ingest_documents()