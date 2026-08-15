from pathlib import Path

from src.ingestion.models import Document


def parse_document(file_path: str, content: str) -> Document:
    path = Path(file_path)

    return Document(
        file_name=path.name,
        file_extension=path.suffix.lower(),
        content=content,
    )