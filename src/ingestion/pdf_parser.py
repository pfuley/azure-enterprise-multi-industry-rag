from pathlib import Path

from pypdf import PdfReader

from src.ingestion.models import Document


def parse_pdf(file_path: str) -> Document:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected PDF file: {file_path}")

    reader = PdfReader(path)

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    content = "\n\n".join(pages)

    return Document(
        file_name=path.name,
        file_extension=".pdf",
        content=content,
        pages=pages,
    )