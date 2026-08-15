from dataclasses import dataclass, field


@dataclass
class Document:
    file_name: str
    file_extension: str
    content: str


@dataclass
class Chunk:
    chunk_id: str
    file_name: str
    content: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)
    embedding: list[float] | None = None