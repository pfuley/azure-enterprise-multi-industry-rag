from openai import OpenAI

from src.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)


def create_rewrite_client() -> OpenAI:
    if not AZURE_OPENAI_ENDPOINT:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")

    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY is not configured")

    return OpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        base_url=f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/v1/",
    )


def rewrite_query(
    question: str,
    conversation_history: list[dict] | None = None,
) -> str:
    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not conversation_history:
        return question

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in conversation_history
    )

    client = create_rewrite_client()

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions="""
You rewrite conversational user questions into standalone search queries.

Rules:
- Use conversation history only to resolve missing context.
- Preserve the user's actual intent.
- Do not answer the question.
- Do not add facts that are not present.
- Return only the rewritten search query.
""".strip(),
        input=f"""
CONVERSATION HISTORY:
{history_text}

LATEST QUESTION:
{question}
""".strip(),
    )

    return response.output_text.strip()