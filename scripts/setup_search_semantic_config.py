from azure.core.credentials import (
    AzureKeyCredential,
)
from azure.search.documents.indexes import (
    SearchIndexClient,
)
from azure.search.documents.indexes.models import (
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)

from src.core.config import (
    AZURE_SEARCH_API_KEY,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_INDEX_NAME,
)


SEMANTIC_CONFIGURATION_NAME = (
    "enterprise-rag-semantic-config"
)


def configure_semantic_search() -> None:

    if not AZURE_SEARCH_ENDPOINT:
        raise ValueError(
            "AZURE_SEARCH_ENDPOINT "
            "is not configured"
        )

    if not AZURE_SEARCH_API_KEY:
        raise ValueError(
            "AZURE_SEARCH_API_KEY "
            "is not configured"
        )

    if not AZURE_SEARCH_INDEX_NAME:
        raise ValueError(
            "AZURE_SEARCH_INDEX_NAME "
            "is not configured"
        )

    client = SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(
            AZURE_SEARCH_API_KEY
        ),
    )

    # -----------------------------------------
    # 1. Load existing index
    #
    # This preserves:
    # - fields
    # - vector configuration
    # - existing index structure
    # - indexed documents
    # -----------------------------------------

    index = client.get_index(
        AZURE_SEARCH_INDEX_NAME
    )

    # -----------------------------------------
    # 2. Define semantic configuration
    #
    # "content" is the natural-language field
    # used by semantic ranking.
    # -----------------------------------------

    semantic_configuration = (
        SemanticConfiguration(
            name=(
                SEMANTIC_CONFIGURATION_NAME
            ),
            prioritized_fields=(
                SemanticPrioritizedFields(
                    content_fields=[
                        SemanticField(
                            field_name="content"
                        )
                    ]
                )
            ),
        )
    )

    # -----------------------------------------
    # 3. Preserve any other existing semantic
    #    configurations
    # -----------------------------------------

    existing_configurations = []

    if (
        index.semantic_search
        and
        index.semantic_search.configurations
    ):
        existing_configurations = [
            configuration
            for configuration
            in (
                index
                .semantic_search
                .configurations
            )
            if (
                configuration.name
                != SEMANTIC_CONFIGURATION_NAME
            )
        ]

    existing_configurations.append(
        semantic_configuration
    )

    # -----------------------------------------
    # 4. Attach semantic search to index
    # -----------------------------------------

    index.semantic_search = (
        SemanticSearch(
            default_configuration_name=(
                SEMANTIC_CONFIGURATION_NAME
            ),
            configurations=(
                existing_configurations
            ),
        )
    )

    # -----------------------------------------
    # 5. Update existing index
    # -----------------------------------------

    client.create_or_update_index(
        index
    )

    print(
        "Semantic configuration created:"
    )

    print(
        SEMANTIC_CONFIGURATION_NAME
    )


if __name__ == "__main__":
    configure_semantic_search()