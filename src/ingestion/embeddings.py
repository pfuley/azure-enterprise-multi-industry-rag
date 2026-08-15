from openai import OpenAI

from src.ingestion.models import Chunk
from src.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)


def create_embedding_client() -> OpenAI:
    if not AZURE_OPENAI_ENDPOINT:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")

    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY is not configured")

    return OpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        base_url=f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/v1/",
    )


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Cannot generate embedding for empty text")

    if not AZURE_OPENAI_EMBEDDING_DEPLOYMENT:
        raise ValueError(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT is not configured"
        )

    client = create_embedding_client()

    response = client.embeddings.create(
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input=text,
    )

    return response.data[0].embedding


def embed_chunk(chunk: Chunk) -> Chunk:
    chunk.embedding = generate_embedding(chunk.content)

    return chunk