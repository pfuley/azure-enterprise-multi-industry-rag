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


def evaluate_answer_relevance(
    question: str,
    answer: str,
) -> dict:

    if not question.strip():
        raise ValueError(
            "Question cannot be empty"
        )

    if not answer.strip():
        return {
            "relevant": False,
            "score": 0,
            "reason": "The answer was empty.",
        }

    client = create_evaluation_client()

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions="""
You are evaluating the answer quality of a
Retrieval-Augmented Generation system.

Determine how well the generated answer addresses
the user's question.

Evaluate relevance only.

Do not evaluate whether the answer is grounded in
the retrieved documents. Groundedness is evaluated
separately.

Return valid JSON only:

{
  "relevant": true,
  "score": 0,
  "reason": "short explanation"
}

Scoring:
0 = completely irrelevant
1 = mostly irrelevant
2 = partially relevant
3 = mostly relevant
4 = directly and fully relevant

Do not include markdown.
""".strip(),
        input=f"""
QUESTION:
{question}

GENERATED ANSWER:
{answer}
""".strip(),
    )

    raw_result = response.output_text.strip()

    try:
        result = json.loads(
            raw_result
        )

    except json.JSONDecodeError as error:
        raise ValueError(
            "Relevance evaluator returned "
            f"invalid JSON: {raw_result}"
        ) from error

    return {
        "relevant": bool(
            result.get(
                "relevant",
                False,
            )
        ),
        "score": int(
            result.get(
                "score",
                0,
            )
        ),
        "reason": result.get(
            "reason",
            "",
        ),
    }