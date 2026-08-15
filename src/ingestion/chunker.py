from src.ingestion.models import Document, Chunk


def chunk_document(
    document: Document,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[Chunk]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    start = 0
    chunk_index = 0

    while start < len(document.content):
        end = start + chunk_size

        chunk_text = document.content[start:end]

        chunk = Chunk(
            chunk_id=f"{document.file_name}-{chunk_index}",
            file_name=document.file_name,
            content=chunk_text,
            chunk_index=chunk_index,
        )

        chunks.append(chunk)

        start += chunk_size - overlap
        chunk_index += 1

    return chunks