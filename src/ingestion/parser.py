from pathlib import Path

from src.ingestion.models import Document
from src.ingestion.pdf_parser import parse_pdf


def parse_text_document(file_path: str, content: str) -> Document:
    path = Path(file_path)

    return Document(
        file_name=path.name,
        file_extension=path.suffix.lower(),
        content=content,
    )


def parse_document(file_path: str, content: str | None = None) -> Document:
    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".pdf":
        return parse_pdf(file_path)

    if extension == ".txt":
        if content is None:
            raise ValueError("Text content is required for TXT files")

        return parse_text_document(
            file_path=file_path,
            content=content,
        )

    raise ValueError(
        f"Unsupported file type: {extension}"
    )