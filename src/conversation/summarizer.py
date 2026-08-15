from openai import OpenAI

from src.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)


def create_summary_client() -> OpenAI:
    if not AZURE_OPENAI_ENDPOINT:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")

    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY is not configured")

    if not AZURE_OPENAI_CHAT_DEPLOYMENT:
        raise ValueError(
            "AZURE_OPENAI_CHAT_DEPLOYMENT is not configured"
        )

    return OpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        base_url=f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/v1/",
    )


def summarize_conversation(
    messages: list[dict],
    existing_summary: str = "",
) -> str:
    if not messages:
        return existing_summary

    conversation_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in messages
    )

    client = create_summary_client()

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions="""
Summarize the conversation for use as future conversational context.

Rules:
- Preserve important facts, topics, decisions, entities, and user intent.
- Do not invent information.
- Do not answer unanswered questions.
- Keep the summary concise.
- Retain context needed to understand future follow-up questions.
""".strip(),
        input=f"""
EXISTING SUMMARY:
{existing_summary or "None"}

NEW CONVERSATION:
{conversation_text}
""".strip(),
    )

    return response.output_text.strip()