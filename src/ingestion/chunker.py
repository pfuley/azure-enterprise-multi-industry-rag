import re

import tiktoken

from src.ingestion.models import Chunk, Document


DEFAULT_ENCODING = "cl100k_base"


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


def _split_sentences(text: str) -> list[str]:
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def _count_tokens(
    text: str,
    encoding_name: str = DEFAULT_ENCODING,
) -> int:
    encoding = tiktoken.get_encoding(encoding_name)

    return len(
        encoding.encode(text)
    )


def _chunk_text_by_tokens(
    text: str,
    file_name: str,
    starting_chunk_index: int,
    max_tokens: int,
    overlap_sentences: int,
    page_number: int | None = None,
) -> list[Chunk]:

    sentences = _split_sentences(text)

    if not sentences:
        return []

    chunks = []

    current_sentences = []
    current_tokens = 0
    chunk_index = starting_chunk_index

    safe_file_name = _safe_file_name(file_name)

    for sentence in sentences:
        sentence_tokens = _count_tokens(sentence)

        if (
            current_sentences
            and current_tokens + sentence_tokens > max_tokens
        ):
            chunk_text = " ".join(current_sentences)

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

            if overlap_sentences > 0:
                current_sentences = current_sentences[
                    -overlap_sentences:
                ]
            else:
                current_sentences = []

            current_tokens = sum(
                _count_tokens(existing_sentence)
                for existing_sentence in current_sentences
            )

        current_sentences.append(sentence)
        current_tokens += sentence_tokens

    if current_sentences:
        chunk_text = " ".join(current_sentences)

        chunks.append(
            Chunk(
                chunk_id=f"{safe_file_name}-{chunk_index}",
                file_name=file_name,
                content=chunk_text,
                chunk_index=chunk_index,
                page_number=page_number,
            )
        )

    return chunks


def chunk_document(
    document: Document,
    chunk_size: int = 300,
    overlap: int = 1,
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
            page_chunks = _chunk_text_by_tokens(
                text=page_text,
                file_name=document.file_name,
                starting_chunk_index=next_chunk_index,
                max_tokens=chunk_size,
                overlap_sentences=overlap,
                page_number=page_index,
            )

            all_chunks.extend(page_chunks)

            next_chunk_index += len(page_chunks)

        return all_chunks

    return _chunk_text_by_tokens(
        text=document.content,
        file_name=document.file_name,
        starting_chunk_index=0,
        max_tokens=chunk_size,
        overlap_sentences=overlap,
    )