from src.ingestion.industry_config import IndustryConfig
from src.ingestion.pipeline import ingest_document


config = IndustryConfig(
    industry="it-support",
    department="service-desk",
    document_type="knowledge-article",
    classification="internal",
    allowed_groups=[
        "service-desk",
        "it-admins",
    ],
    allowed_roles=[
        "employee",
    ],
)

chunks_uploaded = ingest_document(
    file_path="data/it-support/sample.txt",
    config=config,
)

print(
    f"Completed ingestion. "
    f"Uploaded {chunks_uploaded} chunks."
)