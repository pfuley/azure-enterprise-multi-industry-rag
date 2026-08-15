from openai import OpenAI

from src.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)
from src.rag.context_builder import build_context
from src.retrieval.vector_search import semantic_hybrid_search


def create_chat_client() -> OpenAI:
    if not AZURE_OPENAI_ENDPOINT:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")

    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY is not configured")

    return OpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        base_url=f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/v1/",
    )


def answer_question(
    question: str,
    industry: str,
    department: str | None = None,
    classification: str | None = None,
    top_k: int = 3,
) -> dict:
    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not AZURE_OPENAI_CHAT_DEPLOYMENT:
        raise ValueError(
            "AZURE_OPENAI_CHAT_DEPLOYMENT is not configured"
        )

    search_results = semantic_hybrid_search(
        query=question,
        top_k=top_k,
        industry=industry,
        department=department,
        classification=classification,
    )

    if not search_results:
        return {
            "answer": (
                "I could not find sufficient information in the "
                "authorised knowledge base to answer this question."
            ),
            "sources": [],
        }

    context = build_context(search_results)

    client = create_chat_client()

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions="""
You are an enterprise knowledge assistant.

Answer the user's question using only the supplied knowledge-base context.

Rules:
- Do not use outside knowledge.
- Do not invent information.
- If the supplied context does not contain enough information, say so.
- Keep the answer concise and factual.
- Cite supporting sources using [SOURCE: filename].
""".strip(),
        input=f"""
USER QUESTION:
{question}

KNOWLEDGE BASE CONTEXT:
{context}
""".strip(),
    )

    sources = list(
        dict.fromkeys(
            result["file_name"]
            for result in search_results
        )
    )

    return {
        "answer": response.output_text,
        "sources": sources,
    }