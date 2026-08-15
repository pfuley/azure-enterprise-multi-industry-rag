from src.security.token_validator import (
    validate_access_token,
)


token = input(
    "Paste Entra access token: "
).strip()


identity = validate_access_token(
    token
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