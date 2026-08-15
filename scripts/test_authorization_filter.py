from src.security.authorization import AuthorizationContext
from src.security.filters import build_authorization_filter


auth = AuthorizationContext(
    user_id="user-001",
    roles=["employee"],
    groups=[
        "service-desk",
        "it-admins",
    ],
    allowed_industries=[
        "it-support",
    ],
    allowed_departments=[
        "service-desk",
    ],
    max_classification="internal",
)

security_filter = build_authorization_filter(auth)

print("\nAUTHORIZATION FILTER")
print("=" * 60)
print(security_filter)