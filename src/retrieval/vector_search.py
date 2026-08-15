from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from src.core.config import (
    AZURE_SEARCH_API_KEY,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_INDEX_NAME,
)
from src.ingestion.embeddings import generate_embedding
from src.security.authorization import AuthorizationContext
from src.security.filters import build_authorization_filter


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


def build_filter(
    industry: str | None = None,
    department: str | None = None,
    classification: str | None = None,
) -> str | None:
    """
    Legacy metadata filter used by the vector/hybrid test functions.

    The secured semantic RAG path uses AuthorizationContext instead.
    """
    filters = []

    if industry:
        filters.append(
            f"industry eq '{industry.replace(chr(39), chr(39) * 2)}'"
        )

    if department:
        filters.append(
            f"department eq '{department.replace(chr(39), chr(39) * 2)}'"
        )

    if classification:
        filters.append(
            f"classification eq "
            f"'{classification.replace(chr(39), chr(39) * 2)}'"
        )

    if not filters:
        return None

    return " and ".join(filters)


def _format_results(results) -> list[dict]:
    return [
        {
            "chunk_id": result["chunk_id"],
            "content": result["content"],
            "file_name": result["file_name"],
            "chunk_index": result["chunk_index"],
            "page_number": result.get("page_number"),
            "industry": result["industry"],
            "department": result["department"],
            "document_type": result["document_type"],
            "classification": result["classification"],
            "score": result["@search.score"],
            "reranker_score": result.get(
                "@search.reranker_score"
            ),
        }
        for result in results
    ]


def vector_search(
    query: str,
    top_k: int = 3,
    industry: str | None = None,
    department: str | None = None,
    classification: str | None = None,
) -> list[dict]:
    if not query.strip():
        raise ValueError("Search query cannot be empty")

    query_embedding = generate_embedding(query)

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    search_filter = build_filter(
        industry=industry,
        department=department,
        classification=classification,
    )

    client = create_search_client()

    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        filter=search_filter,
        select=[
            "chunk_id",
            "content",
            "file_name",
            "chunk_index",
            "page_number",
            "industry",
            "department",
            "document_type",
            "classification",
        ],
        top=top_k,
    )

    return _format_results(results)


def hybrid_search(
    query: str,
    top_k: int = 3,
    industry: str | None = None,
    department: str | None = None,
    classification: str | None = None,
) -> list[dict]:
    if not query.strip():
        raise ValueError("Search query cannot be empty")

    query_embedding = generate_embedding(query)

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    search_filter = build_filter(
        industry=industry,
        department=department,
        classification=classification,
    )

    client = create_search_client()

    results = client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=search_filter,
        select=[
            "chunk_id",
            "content",
            "file_name",
            "chunk_index",
            "page_number",
            "industry",
            "department",
            "document_type",
            "classification",
        ],
        top=top_k,
    )

    return _format_results(results)


def semantic_hybrid_search(
    query: str,
    top_k: int = 3,
    auth: AuthorizationContext | None = None,
) -> list[dict]:
    if not query.strip():
        raise ValueError("Search query cannot be empty")

    query_embedding = generate_embedding(query)

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=50,
        fields="embedding",
    )

    search_filter = (
        build_authorization_filter(auth)
        if auth
        else None
    )

    client = create_search_client()

    results = client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=search_filter,
        query_type="semantic",
        semantic_configuration_name="semantic-config",
        select=[
            "chunk_id",
            "content",
            "file_name",
            "chunk_index",
            "page_number",
            "industry",
            "department",
            "document_type",
            "classification",
            "allowed_groups",
            "allowed_roles",
        ],
        top=top_k,
    )

    return _format_results(results)