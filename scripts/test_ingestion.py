from src.ingestion.loader import load_text_file
from src.ingestion.parser import parse_document
from src.ingestion.chunker import chunk_document
from src.ingestion.metadata import enrich_chunk_metadata
from src.ingestion.embeddings import embed_chunk
from src.search.uploader import upload_chunks


file_path = "data/sample.txt"

content = load_text_file(file_path)

document = parse_document(
    file_path,
    content,
)

chunks = chunk_document(
    document,
    chunk_size=500,
    overlap=100,
)

for chunk in chunks:
    enrich_chunk_metadata(
        chunk,
        industry="it-support",
        department="service-desk",
        document_type="knowledge-article",
        classification="internal",
    )

    embed_chunk(chunk)

upload_chunks(chunks)