import requests

from src.core.config import (
    AZURE_CONTENT_SAFETY_API_KEY,
    AZURE_CONTENT_SAFETY_BLOCKLIST_NAME,
    AZURE_CONTENT_SAFETY_ENDPOINT,
)
from src.guardrails.models import ContentSafetyResult


CONTENT_SAFETY_API_VERSION = "2024-09-01"


def analyze_text_safety(
    text: str,
) -> ContentSafetyResult:

    # -----------------------------------------
    # 1. Validate input
    # -----------------------------------------

    if not text.strip():
        raise ValueError(
            "Text cannot be empty"
        )

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

    # -----------------------------------------
    # 2. Build Azure Content Safety endpoint
    # -----------------------------------------

    url = (
        f"{AZURE_CONTENT_SAFETY_ENDPOINT.rstrip('/')}"
        "/contentsafety/text:analyze"
        f"?api-version={CONTENT_SAFETY_API_VERSION}"
    )

    # -----------------------------------------
    # 3. Build request payload
    # -----------------------------------------

    payload = {
        "text": text,
    }

    # If an enterprise blocklist is configured,
    # ask Azure Content Safety to evaluate it.
    if AZURE_CONTENT_SAFETY_BLOCKLIST_NAME:
        payload["blocklistNames"] = [
            AZURE_CONTENT_SAFETY_BLOCKLIST_NAME
        ]

        # Continue normal category analysis even
        # when a blocklist match is detected.
        payload["haltOnBlocklistHit"] = False

    # -----------------------------------------
    # 4. Build HTTP headers
    # -----------------------------------------

    headers = {
        "Ocp-Apim-Subscription-Key":
            AZURE_CONTENT_SAFETY_API_KEY,
        "Content-Type":
            "application/json",
    }

    # -----------------------------------------
    # 5. Call Azure AI Content Safety
    # -----------------------------------------

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    result = response.json()

    # -----------------------------------------
    # 6. Parse harmful-content categories
    # -----------------------------------------

    categories = {
        item["category"]:
            item["severity"]
        for item in result.get(
            "categoriesAnalysis",
            []
        )
    }

    # -----------------------------------------
    # 7. Parse enterprise blocklist matches
    # -----------------------------------------

    blocklist_matches = [
        match.get(
            "blocklistItemText",
            ""
        )
        for match in result.get(
            "blocklistsMatch",
            []
        )
        if match.get(
            "blocklistItemText"
        )
    ]

    # -----------------------------------------
    # 8. Convert Azure response into our
    #    application data model
    # -----------------------------------------

    return ContentSafetyResult(
        hate=categories.get(
            "Hate",
            0,
        ),
        self_harm=categories.get(
            "SelfHarm",
            0,
        ),
        sexual=categories.get(
            "Sexual",
            0,
        ),
        violence=categories.get(
            "Violence",
            0,
        ),
        blocklist_matches=blocklist_matches,
    )