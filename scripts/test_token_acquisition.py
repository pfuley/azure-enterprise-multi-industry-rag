import msal

from src.core.config import (
    AZURE_ENTRA_API_CLIENT_ID,
    AZURE_ENTRA_TENANT_ID,
    AZURE_ENTRA_TEST_CLIENT_ID,
)
from src.security.token_validator import validate_access_token


if not AZURE_ENTRA_TENANT_ID:
    raise ValueError(
        "AZURE_ENTRA_TENANT_ID is not configured"
    )

if not AZURE_ENTRA_API_CLIENT_ID:
    raise ValueError(
        "AZURE_ENTRA_API_CLIENT_ID is not configured"
    )

if not AZURE_ENTRA_TEST_CLIENT_ID:
    raise ValueError(
        "AZURE_ENTRA_TEST_CLIENT_ID is not configured"
    )


authority = (
    "https://login.microsoftonline.com/"
    f"{AZURE_ENTRA_TENANT_ID}"
)


scope = (
    f"api://{AZURE_ENTRA_API_CLIENT_ID}/RAG.Access"
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
        "Failed to create device flow."
    )


print("\nSIGN IN")
print("=" * 60)

print(flow["message"])


result = client.acquire_token_by_device_flow(
    flow
)


if "access_token" not in result:
    print("\nTOKEN ACQUISITION FAILED")
    print("=" * 60)

    print(
        "Error:",
        result.get("error"),
    )

    print(
        "Description:",
        result.get("error_description"),
    )

    raise RuntimeError(
        "Unable to acquire access token."
    )


access_token = result["access_token"]
print("\nACCESS TOKEN")
print("=" * 60)
print(access_token)

# import jwt

# unverified_claims = jwt.decode(
#     access_token,
#     options={
#         "verify_signature": False,
#         "verify_aud": False,
#     },
# )

# print("\nTOKEN INFORMATION")
# print("=" * 60)
# print("Version:", unverified_claims.get("ver"))
# print("Issuer:", unverified_claims.get("iss"))
# print("Audience:", unverified_claims.get("aud"))
# print("Scopes:", unverified_claims.get("scp"))
# print("Roles:", unverified_claims.get("roles"))


print("\nTOKEN ACQUIRED")
print("=" * 60)

print(
    "Access token received successfully."
)


identity = validate_access_token(
    access_token
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
    "Roles:",
    identity.roles,
)

print(
    "Groups:",
    identity.groups,
)

print(
    "Authenticated:",
    identity.authenticated,
)