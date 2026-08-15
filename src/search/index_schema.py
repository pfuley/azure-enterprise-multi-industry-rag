from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

from src.core.config import (
    AZURE_SEARCH_API_KEY,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_INDEX_NAME,
)


VECTOR_DIMENSIONS = 1536


def create_index_client() -> SearchIndexClient:
    if not AZURE_SEARCH_ENDPOINT:
        raise ValueError("AZURE_SEARCH_ENDPOINT is not configured")

    if not AZURE_SEARCH_API_KEY:
        raise ValueError("AZURE_SEARCH_API_KEY is not configured")

    return SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY),
    )


def build_index_schema() -> SearchIndex:
    fields = [
        SimpleField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
        ),

        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
        ),

        SimpleField(
            name="file_name",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        SimpleField(
            name="chunk_index",
            type=SearchFieldDataType.Int32,
            filterable=True,
        ),

        SimpleField(
            name="industry",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),

        SimpleField(
            name="department",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),

        SimpleField(
            name="document_type",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),

        SimpleField(
            name="classification",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(
                SearchFieldDataType.Single
            ),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name="vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config",
            )
        ],
    )

    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    content_fields=[
                        SemanticField(
                            field_name="content"
                        )
                    ]
                ),
            )
        ]
    )

    return SearchIndex(
        name=AZURE_SEARCH_INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )


def create_search_index() -> None:
    if not AZURE_SEARCH_INDEX_NAME:
        raise ValueError("AZURE_SEARCH_INDEX_NAME is not configured")

    client = create_index_client()

    index = build_index_schema()

    client.create_or_update_index(index)

    print(
        f"Search index created or updated: "
        f"{AZURE_SEARCH_INDEX_NAME}"
    )