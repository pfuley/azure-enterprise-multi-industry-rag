from src.ingestion.models import Chunk, Document


def _validate_chunk_settings(
    chunk_size: int,
    overlap: int,
) -> None:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")


def _safe_file_name(file_name: str) -> str:
    return file_name.replace(".", "_")


def _chunk_text(
    text: str,
    file_name: str,
    starting_chunk_index: int,
    chunk_size: int,
    overlap: int,
    page_number: int | None = None,
) -> list[Chunk]:

    chunks = []

    start = 0
    chunk_index = starting_chunk_index

    safe_file_name = _safe_file_name(file_name)

    while start < len(text):
        end = start + chunk_size

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                Chunk(
                    chunk_id=f"{safe_file_name}-{chunk_index}",
                    file_name=file_name,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    page_number=page_number,
                )
            )

            chunk_index += 1

        start += chunk_size - overlap

    return chunks


def chunk_document(
    document: Document,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[Chunk]:

    _validate_chunk_settings(
        chunk_size=chunk_size,
        overlap=overlap,
    )

    all_chunks = []

    if document.pages:
        next_chunk_index = 0

        for page_index, page_text in enumerate(
            document.pages,
            start=1,
        ):
            page_chunks = _chunk_text(
                text=page_text,
                file_name=document.file_name,
                starting_chunk_index=next_chunk_index,
                chunk_size=chunk_size,
                overlap=overlap,
                page_number=page_index,
            )

            all_chunks.extend(page_chunks)

            next_chunk_index += len(page_chunks)

        return all_chunks

    return _chunk_text(
        text=document.content,
        file_name=document.file_name,
        starting_chunk_index=0,
        chunk_size=chunk_size,
        overlap=overlap,
    )