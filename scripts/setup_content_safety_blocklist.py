import requests

from src.core.config import (
    AZURE_CONTENT_SAFETY_API_KEY,
    AZURE_CONTENT_SAFETY_BLOCKLIST_NAME,
    AZURE_CONTENT_SAFETY_ENDPOINT,
)


API_VERSION = "2024-09-01"


def create_or_update_blocklist() -> None:
    if not AZURE_CONTENT_SAFETY_ENDPOINT:
        raise ValueError(
            "AZURE_CONTENT_SAFETY_ENDPOINT is not configured"
        )

    if not AZURE_CONTENT_SAFETY_API_KEY:
        raise ValueError(
            "AZURE_CONTENT_SAFETY_API_KEY is not configured"
        )

    if not AZURE_CONTENT_SAFETY_BLOCKLIST_NAME:
        raise ValueError(
            "AZURE_CONTENT_SAFETY_BLOCKLIST_NAME is not configured"
        )

    endpoint = AZURE_CONTENT_SAFETY_ENDPOINT.rstrip("/")

    headers = {
        "Ocp-Apim-Subscription-Key":
            AZURE_CONTENT_SAFETY_API_KEY,
        "Content-Type":
            "application/merge-patch+json",
    }

    url = (
        f"{endpoint}"
        "/contentsafety/text/blocklists/"
        f"{AZURE_CONTENT_SAFETY_BLOCKLIST_NAME}"
        f"?api-version={API_VERSION}"
    )

    response = requests.patch(
        url,
        headers=headers,
        json={
            "description":
                "Enterprise RAG custom safety blocklist"
        },
        timeout=15,
    )

    response.raise_for_status()

    print(
        "Blocklist created or updated:",
        AZURE_CONTENT_SAFETY_BLOCKLIST_NAME,
    )


def add_test_blocklist_item() -> None:
    endpoint = AZURE_CONTENT_SAFETY_ENDPOINT.rstrip("/")

    headers = {
        "Ocp-Apim-Subscription-Key":
            AZURE_CONTENT_SAFETY_API_KEY,
        "Content-Type":
            "application/json",
    }

    url = (
        f"{endpoint}"
        "/contentsafety/text/blocklists/"
        f"{AZURE_CONTENT_SAFETY_BLOCKLIST_NAME}"
        ":addOrUpdateBlocklistItems"
        f"?api-version={API_VERSION}"
    )

    payload = {
        "blocklistItems": [
            {
                "text": "BLOCKME123",
                "description":
                    "Harmless development test term",
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    result = response.json()

    print("Blocklist item added.")

    for item in result.get(
        "blocklistItems",
        []
    ):
        print(
            "Item:",
            item.get("text"),
        )

        print(
            "ID:",
            item.get("blocklistItemId"),
        )


if __name__ == "__main__":
    create_or_update_blocklist()
    add_test_blocklist_item()