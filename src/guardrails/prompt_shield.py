import requests

from src.core.config import (
    AZURE_CONTENT_SAFETY_API_KEY,
    AZURE_CONTENT_SAFETY_ENDPOINT,
)
from src.guardrails.models import (
    PromptShieldResult,
)


PROMPT_SHIELD_API_VERSION = "2024-09-01"

MAX_DOCUMENTS = 5
MAX_DOCUMENT_CHARACTERS = 10000


def _prepare_documents(
    documents: list[str] | None,
) -> list[str]:

    if not documents:
        return []

    prepared_documents = []

    remaining_characters = (
        MAX_DOCUMENT_CHARACTERS
    )

    for document in documents[
        :MAX_DOCUMENTS
    ]:

        if remaining_characters <= 0:
            break

        if not document:
            continue

        trimmed_document = document[
            :remaining_characters
        ]

        if trimmed_document.strip():
            prepared_documents.append(
                trimmed_document
            )

            remaining_characters -= len(
                trimmed_document
            )

    return prepared_documents


def analyze_prompt_shield(
    user_prompt: str,
    documents: list[str] | None = None,
) -> PromptShieldResult:

    # -----------------------------------------
    # 1. Validate configuration
    # -----------------------------------------

    if not AZURE_CONTENT_SAFETY_ENDPOINT:
        raise ValueError(
            "AZURE_CONTENT_SAFETY_ENDPOINT "
            "is not configured"
        )

    if not AZURE_CONTENT_SAFETY_API_KEY:
        raise ValueError(
            "AZURE_CONTENT_SAFETY_API_KEY "
            "is not configured"
        )

    if not user_prompt.strip():
        raise ValueError(
            "User prompt cannot be empty"
        )

    # -----------------------------------------
    # 2. Respect Prompt Shields input limits
    # -----------------------------------------

    safe_user_prompt = user_prompt[
        :10000
    ]

    prepared_documents = (
        _prepare_documents(
            documents
        )
    )

    # -----------------------------------------
    # 3. Build endpoint
    # -----------------------------------------

    url = (
        f"{AZURE_CONTENT_SAFETY_ENDPOINT.rstrip('/')}"
        "/contentsafety/text:shieldPrompt"
        f"?api-version="
        f"{PROMPT_SHIELD_API_VERSION}"
    )

    # -----------------------------------------
    # 4. Build request
    # -----------------------------------------

    payload = {
        "userPrompt":
            safe_user_prompt,

        "documents":
            prepared_documents,
    }

    headers = {
        "Ocp-Apim-Subscription-Key":
            AZURE_CONTENT_SAFETY_API_KEY,

        "Content-Type":
            "application/json",
    }

    # -----------------------------------------
    # 5. Call Azure Content Safety
    # -----------------------------------------

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=15,
    )

    # Helpful error when Azure rejects request.
    if not response.ok:
        raise RuntimeError(
            "Prompt Shield request failed. "
            f"Status: {response.status_code}. "
            f"Response: {response.text}"
        )

    result = response.json()

    # -----------------------------------------
    # 6. Parse user-prompt analysis
    # -----------------------------------------

    user_prompt_analysis = result.get(
        "userPromptAnalysis",
        {},
    )

    user_prompt_attack = (
        user_prompt_analysis.get(
            "attackDetected",
            False,
        )
    )

    # -----------------------------------------
    # 7. Parse document analyses
    # -----------------------------------------

    document_analyses = result.get(
        "documentsAnalysis",
        [],
    )

    document_attack = any(
        document.get(
            "attackDetected",
            False,
        )
        for document in document_analyses
    )

    # -----------------------------------------
    # 8. Return application model
    # -----------------------------------------

    return PromptShieldResult(
        user_prompt_attack=(
            user_prompt_attack
        ),
        document_attack=(
            document_attack
        ),
    )