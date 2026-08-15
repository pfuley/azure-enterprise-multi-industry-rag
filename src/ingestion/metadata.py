from src.ingestion.models import Chunk


def enrich_chunk_metadata(
    chunk: Chunk,
    industry: str,
    department: str,
    document_type: str,
    classification: str = "internal",
) -> Chunk:

    chunk.metadata.update(
        {
            "industry": industry,
            "department": department,
            "document_type": document_type,
            "classification": classification,
        }
    )

    return chunk