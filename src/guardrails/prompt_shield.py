import requests

from src.core.config import (
    AZURE_CONTENT_SAFETY_API_KEY,
    AZURE_CONTENT_SAFETY_ENDPOINT,
)
from src.guardrails.models import PromptShieldResult


PROMPT_SHIELD_API_VERSION = "2024-09-01"


def analyze_prompt_shield(
    user_prompt: str,
    documents: list[str] | None = None,
) -> PromptShieldResult:

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

    url = (
        f"{AZURE_CONTENT_SAFETY_ENDPOINT.rstrip('/')}"
        "/contentsafety/text:shieldPrompt"
        f"?api-version={PROMPT_SHIELD_API_VERSION}"
    )

    payload = {
        "userPrompt": user_prompt,
        "documents": documents or [],
    }

    headers = {
        "Ocp-Apim-Subscription-Key":
            AZURE_CONTENT_SAFETY_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    result = response.json()

    user_prompt_analysis = result.get(
        "userPromptAnalysis",
        {},
    )

    document_analyses = result.get(
        "documentsAnalysis",
        [],
    )

    user_prompt_attack = (
        user_prompt_analysis.get(
            "attackDetected",
            False,
        )
    )

    document_attack = any(
        document.get(
            "attackDetected",
            False,
        )
        for document in document_analyses
    )

    return PromptShieldResult(
        user_prompt_attack=user_prompt_attack,
        document_attack=document_attack,
    )