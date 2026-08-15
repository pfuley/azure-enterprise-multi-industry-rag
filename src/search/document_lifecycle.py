from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from src.core.config import (
    AZURE_SEARCH_API_KEY,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_INDEX_NAME,
)


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


def delete_existing_document_chunks(
    file_name: str,
) -> int:
    client = create_search_client()

    safe_file_name = file_name.replace("'", "''")

    results = client.search(
        search_text="*",
        filter=f"file_name eq '{safe_file_name}'",
        select=["chunk_id"],
    )

    documents_to_delete = [
        {
            "chunk_id": result["chunk_id"]
        }
        for result in results
    ]

    if not documents_to_delete:
        return 0

    delete_results = client.delete_documents(
        documents=documents_to_delete
    )

    failed = [
        result
        for result in delete_results
        if not result.succeeded
    ]

    if failed:
        failed_keys = [
            result.key
            for result in failed
        ]

        raise RuntimeError(
            "Failed to delete stale chunks: "
            f"{failed_keys}"
        )

    return len(documents_to_delete)