from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from src.api.exceptions import APIServiceError
from src.core.config import (
    AZURE_SEARCH_API_KEY,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_INDEX_NAME,
)
from src.ingestion.embeddings import generate_embedding
from src.security.authorization import AuthorizationContext
from src.security.filters import build_authorization_filter


SEMANTIC_CONFIGURATION_NAME = (
    "enterprise-rag-semantic-config"
)


def create_search_client() -> SearchClient:
    if not AZURE_SEARCH_ENDPOINT:
        raise ValueError(
            "AZURE_SEARCH_ENDPOINT is not configured"
        )

    if not AZURE_SEARCH_INDEX_NAME:
        raise ValueError(
            "AZURE_SEARCH_INDEX_NAME is not configured"
        )

    if not AZURE_SEARCH_API_KEY:
        raise ValueError(
            "AZURE_SEARCH_API_KEY is not configured"
        )

    return SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(
            AZURE_SEARCH_API_KEY
        ),
    )


def _escape_odata_value(
    value: str,
) -> str:
    return value.replace(
        "'",
        "''",
    )


def _build_legacy_filter(
    industry: str | None = None,
    department: str | None = None,
    classification: str | None = None,
) -> str | None:
    """
    Build filters for the older retrieval interface
    used by scripts/test_vector_search.py.

    This preserves existing project tests while the
    production RAG path continues to use
    AuthorizationContext.
    """

    filters = []

    if industry:
        filters.append(
            "industry eq "
            f"'{_escape_odata_value(industry)}'"
        )

    if department:
        filters.append(
            "department eq "
            f"'{_escape_odata_value(department)}'"
        )

    if classification:
        filters.append(
            "classification eq "
            f"'{_escape_odata_value(classification)}'"
        )

    if not filters:
        return None

    return " and ".join(
        filters
    )


def _resolve_filter(
    auth: AuthorizationContext | None,
    industry: str | None,
    department: str | None,
    classification: str | None,
) -> str | None:
    """
    Production calls use AuthorizationContext.

    Older standalone retrieval tests can still
    supply direct metadata filters.
    """

    if auth is not None:
        return build_authorization_filter(
            auth
        )

    return _build_legacy_filter(
        industry=industry,
        department=department,
        classification=classification,
    )


def _format_results(
    results,
) -> list[dict]:

    formatted_results = []

    for result in results:
        formatted_results.append(
            {
                "chunk_id":
                    result.get(
                        "chunk_id"
                    ),

                "content":
                    result.get(
                        "content"
                    ),

                "file_name":
                    result.get(
                        "file_name"
                    ),

                "page_number":
                    result.get(
                        "page_number"
                    ),

                "industry":
                    result.get(
                        "industry"
                    ),

                "department":
                    result.get(
                        "department"
                    ),

                "classification":
                    result.get(
                        "classification"
                    ),

                "allowed_groups":
                    result.get(
                        "allowed_groups",
                        [],
                    ),

                "allowed_roles":
                    result.get(
                        "allowed_roles",
                        [],
                    ),

                "score":
                    result.get(
                        "@search.score"
                    ),

                "reranker_score":
                    result.get(
                        "@search.reranker_score"
                    ),
            }
        )

    return formatted_results


def vector_search(
    query: str,
    top_k: int = 3,
    industry: str | None = None,
    department: str | None = None,
    classification: str | None = None,
    auth: AuthorizationContext | None = None,
) -> list[dict]:

    if not query.strip():
        raise ValueError(
            "Search query cannot be empty"
        )

    try:
        search_client = (
            create_search_client()
        )

        query_embedding = (
            generate_embedding(
                query
            )
        )

        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields="embedding",
        )

        search_filter = _resolve_filter(
            auth=auth,
            industry=industry,
            department=department,
            classification=classification,
        )

        results = search_client.search(
            search_text=None,
            vector_queries=[
                vector_query
            ],
            filter=search_filter,
            select=[
                "chunk_id",
                "content",
                "file_name",
                "page_number",
                "industry",
                "department",
                "classification",
                "allowed_groups",
                "allowed_roles",
            ],
            top=top_k,
        )

        return _format_results(
            results
        )

    except APIServiceError:
        raise

    except AzureError as error:
        raise APIServiceError(
            error_code=(
                "retrieval_service_unavailable"
            ),
            message=(
                "The knowledge retrieval service "
                "is temporarily unavailable."
            ),
        ) from error


def hybrid_search(
    query: str,
    top_k: int = 3,
    industry: str | None = None,
    department: str | None = None,
    classification: str | None = None,
    auth: AuthorizationContext | None = None,
) -> list[dict]:

    if not query.strip():
        raise ValueError(
            "Search query cannot be empty"
        )

    try:
        search_client = (
            create_search_client()
        )

        query_embedding = (
            generate_embedding(
                query
            )
        )

        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields="embedding",
        )

        search_filter = _resolve_filter(
            auth=auth,
            industry=industry,
            department=department,
            classification=classification,
        )

        results = search_client.search(
            search_text=query,
            vector_queries=[
                vector_query
            ],
            filter=search_filter,
            select=[
                "chunk_id",
                "content",
                "file_name",
                "page_number",
                "industry",
                "department",
                "classification",
                "allowed_groups",
                "allowed_roles",
            ],
            top=top_k,
        )

        return _format_results(
            results
        )

    except APIServiceError:
        raise

    except AzureError as error:
        raise APIServiceError(
            error_code=(
                "retrieval_service_unavailable"
            ),
            message=(
                "The knowledge retrieval service "
                "is temporarily unavailable."
            ),
        ) from error


def semantic_hybrid_search(
    query: str,
    top_k: int = 3,
    auth: AuthorizationContext | None = None,
    industry: str | None = None,
    department: str | None = None,
    classification: str | None = None,
) -> list[dict]:

    if not query.strip():
        raise ValueError(
            "Search query cannot be empty"
        )

    try:
        search_client = (
            create_search_client()
        )

        query_embedding = (
            generate_embedding(
                query
            )
        )

        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields="embedding",
        )

        search_filter = _resolve_filter(
            auth=auth,
            industry=industry,
            department=department,
            classification=classification,
        )

        results = search_client.search(
            search_text=query,
            vector_queries=[
                vector_query
            ],
            filter=search_filter,
            query_type="semantic",
            semantic_configuration_name=(
                SEMANTIC_CONFIGURATION_NAME
            ),
            select=[
                "chunk_id",
                "content",
                "file_name",
                "page_number",
                "industry",
                "department",
                "classification",
                "allowed_groups",
                "allowed_roles",
            ],
            top=top_k,
        )

        # Azure Search executes lazily when the
        # result iterator is consumed, so this
        # must remain inside the try block.
        return _format_results(
            results
        )

    except APIServiceError:
        raise

    except AzureError as error:
        raise APIServiceError(
            error_code=(
                "retrieval_service_unavailable"
            ),
            message=(
                "The knowledge retrieval service "
                "is temporarily unavailable."
            ),
        ) from error