import json

from openai import OpenAI

from src.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)


def create_evaluation_client() -> OpenAI:
    if not AZURE_OPENAI_ENDPOINT:
        raise ValueError(
            "AZURE_OPENAI_ENDPOINT is not configured"
        )

    if not AZURE_OPENAI_API_KEY:
        raise ValueError(
            "AZURE_OPENAI_API_KEY is not configured"
        )

    if not AZURE_OPENAI_CHAT_DEPLOYMENT:
        raise ValueError(
            "AZURE_OPENAI_CHAT_DEPLOYMENT is not configured"
        )

    return OpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        base_url=(
            f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}"
            "/openai/v1/"
        ),
    )


def evaluate_groundedness(
    question: str,
    answer: str,
    context: str,
) -> dict:
    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not answer.strip():
        raise ValueError("Answer cannot be empty")

    if not context.strip():
        return {
            "grounded": False,
            "score": 0,
            "reason": (
                "No retrieved context was available "
                "to support the answer."
            ),
        }

    client = create_evaluation_client()

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions="""
You are evaluating a Retrieval-Augmented Generation system.

Determine whether the generated answer is supported by the
retrieved knowledge-base context.

Do not judge whether the answer is generally true.
Judge only whether it is supported by the supplied context.

Return valid JSON only using this structure:

{
  "grounded": true,
  "score": 0,
  "reason": "short explanation"
}

Scoring:
0 = unsupported
1 = mostly unsupported
2 = partially supported
3 = mostly supported
4 = fully supported

Do not include markdown.
""".strip(),
        input=f"""
QUESTION:
{question}

GENERATED ANSWER:
{answer}

RETRIEVED CONTEXT:
{context}
""".strip(),
    )

    raw_result = response.output_text.strip()

    try:
        result = json.loads(raw_result)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Groundedness evaluator returned invalid JSON: "
            f"{raw_result}"
        ) from error

    return {
        "grounded": bool(
            result.get("grounded", False)
        ),
        "score": int(
            result.get("score", 0)
        ),
        "reason": result.get(
            "reason",
            "",
        ),
    }