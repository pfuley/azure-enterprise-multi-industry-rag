from src.security.access_policy import (
    build_authorization_context,
)
from src.security.identity import UserIdentity


identity = UserIdentity(
    user_id="entra-test-user-001",
    display_name="Test User",
    email="test@example.com",
    roles=[
        "employee",
    ],
    groups=[
        "service-desk",
    ],
    authenticated=True,
)


authorization = build_authorization_context(
    identity
)


print("\nIDENTITY")
print("=" * 60)

print("User ID:", identity.user_id)
print("Name:", identity.display_name)
print("Email:", identity.email)
print("Roles:", identity.roles)
print("Groups:", identity.groups)
print(
    "Authenticated:",
    identity.authenticated,
)


print("\nAUTHORIZATION")
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