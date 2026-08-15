from dataclasses import dataclass, field


@dataclass
class Document:
    file_name: str
    file_extension: str
    content: str
    pages: list[str] = field(default_factory=list)


@dataclass
class Chunk:
    chunk_id: str
    file_name: str
    content: str
    chunk_index: int
    page_number: int | None = None
    metadata: dict = field(default_factory=dict)
    embedding: list[float] | None = None