import msal

from src.core.config import (
    AZURE_ENTRA_API_CLIENT_ID,
    AZURE_ENTRA_TENANT_ID,
    AZURE_ENTRA_TEST_CLIENT_ID,
)
from src.rag.chat_service import RAGChatService
from src.security.access_policy import (
    build_authorization_context,
)
from src.security.token_validator import (
    validate_access_token,
)


authority = (
    "https://login.microsoftonline.com/"
    f"{AZURE_ENTRA_TENANT_ID}"
)

scope = (
    f"api://{AZURE_ENTRA_API_CLIENT_ID}"
    "/RAG.Access"
)


client = msal.PublicClientApplication(
    client_id=AZURE_ENTRA_TEST_CLIENT_ID,
    authority=authority,
)


flow = client.initiate_device_flow(
    scopes=[scope]
)


if "user_code" not in flow:
    raise RuntimeError(
        "Unable to start Entra device login."
    )


print("\nSIGN IN")
print("=" * 60)
print(flow["message"])


token_result = (
    client.acquire_token_by_device_flow(
        flow
    )
)


if "access_token" not in token_result:
    raise RuntimeError(
        token_result.get(
            "error_description",
            "Unable to acquire token.",
        )
    )


# -------------------------------------------------
# 1. Validate Microsoft Entra token
# -------------------------------------------------

identity = validate_access_token(
    token_result["access_token"]
)


# -------------------------------------------------
# 2. Convert identity to RAG permissions
# -------------------------------------------------

authorization = (
    build_authorization_context(
        identity
    )
)


# -------------------------------------------------
# 3. Create secure conversational RAG
# -------------------------------------------------

chat = RAGChatService(
    auth=authorization
)


# -------------------------------------------------
# 4. Ask question
# -------------------------------------------------

question = (
    "What is retrieval augmented generation?"
)

result = chat.ask(
    question
)


print("\nVALIDATED IDENTITY")
print("=" * 60)

print(
    "User ID:",
    identity.user_id,
)

print(
    "Name:",
    identity.display_name,
)

print(
    "Email:",
    identity.email,
)

print(
    "Entra Roles:",
    identity.roles,
)

print(
    "Entra Groups:",
    identity.groups,
)


print("\nAUTHORIZATION CONTEXT")
print("=" * 60)

print(
    "Allowed Industries:",
    authorization.allowed_industries,
)

print(
    "Allowed Departments:",
    authorization.allowed_departments,
)

print(
    "Maximum Classification:",
    authorization.max_classification,
)


print("\nQUESTION")
print("=" * 60)

print(question)


print("\nSEARCH QUERY")
print("=" * 60)

print(
    result["search_query"]
)


print("\nANSWER")
print("=" * 60)

print(
    result["answer"]
)


print("\nSOURCES")
print("=" * 60)

for source in result["sources"]:
    print(
        f"{source['file_name']} | "
        f"Page: {source['page_number']} | "
        f"Chunk: {source['chunk_id']}"
    )