from pathlib import Path

from src.ingestion.chunker import chunk_document
from src.ingestion.embeddings import embed_chunk
from src.ingestion.industry_config import IndustryConfig
from src.ingestion.loader import load_text_file
from src.ingestion.metadata import enrich_chunk_metadata
from src.ingestion.parser import parse_document
from src.search.uploader import upload_chunks


def ingest_document(
    file_path: str,
    config: IndustryConfig,
    chunk_size: int = 500,
    overlap: int = 100,
) -> int:

    extension = Path(file_path).suffix.lower()

    if extension == ".txt":
        content = load_text_file(file_path)

        document = parse_document(
            file_path=file_path,
            content=content,
        )

    elif extension == ".pdf":
        document = parse_document(
            file_path=file_path,
        )

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    chunks = chunk_document(
        document=document,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    for chunk in chunks:
        enrich_chunk_metadata(
            chunk=chunk,
            industry=config.industry,
            department=config.department,
            document_type=config.document_type,
            classification=config.classification,
        )

        embed_chunk(chunk)

    upload_chunks(chunks)

    return len(chunks)