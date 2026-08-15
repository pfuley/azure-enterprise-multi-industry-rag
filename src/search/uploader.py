from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from src.core.config import (
    AZURE_SEARCH_API_KEY,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_INDEX_NAME,
)
from src.ingestion.models import Chunk


def create_search_client() -> SearchClient:
    if not AZURE_SEARCH_ENDPOINT:
        raise ValueError("AZURE_SEARCH_ENDPOINT is not configured")

    if not AZURE_SEARCH_INDEX_NAME:
        raise ValueError("AZURE_SEARCH_INDEX_NAME is not configured")

    if not AZURE_SEARCH_API_KEY:
        raise ValueError("AZURE_SEARCH_API_KEY is not configured")

    return SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY),
    )


def chunk_to_search_document(chunk: Chunk) -> dict:
    if chunk.embedding is None:
        raise ValueError(
            f"Chunk {chunk.chunk_id} does not contain an embedding"
        )

    return {
        "chunk_id": chunk.chunk_id,
        "content": chunk.content,
        "file_name": chunk.file_name,
        "chunk_index": chunk.chunk_index,
        "industry": chunk.metadata.get("industry"),
        "department": chunk.metadata.get("department"),
        "document_type": chunk.metadata.get("document_type"),
        "classification": chunk.metadata.get("classification"),
        "embedding": chunk.embedding,
    }


def upload_chunks(chunks: list[Chunk]) -> None:
    if not chunks:
        raise ValueError("No chunks provided for upload")

    search_client = create_search_client()

    documents = [
        chunk_to_search_document(chunk)
        for chunk in chunks
    ]

    results = search_client.upload_documents(
        documents=documents
    )

    for result in results:
        if not result.succeeded:
            raise RuntimeError(
                f"Failed to upload document: {result.key}"
            )

    print(f"Uploaded {len(documents)} chunks to Azure AI Search")