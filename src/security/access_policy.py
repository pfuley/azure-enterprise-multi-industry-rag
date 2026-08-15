from src.security.authorization import AuthorizationContext
from src.security.identity import UserIdentity


CLASSIFICATION_LEVELS = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3,
}


ROLE_ACCESS_POLICIES = {
    "RAG.Employee": {
        "industries": [
            "it-support",
        ],
        "departments": [
            "service-desk",
        ],
        "max_classification": "internal",
    },

    "RAG.Admin": {
        "industries": [
            "it-support",
            "financial-services",
            "government",
        ],
        "departments": [
            "service-desk",
            "finance",
            "government-services",
        ],
        "max_classification": "restricted",
    },
}


GROUP_ACCESS_POLICIES = {
    "service-desk": {
        "industries": [
            "it-support",
        ],
        "departments": [
            "service-desk",
        ],
        "max_classification": "internal",
    },

    "it-admins": {
        "industries": [
            "it-support",
        ],
        "departments": [
            "service-desk",
        ],
        "max_classification": "confidential",
    },

    "finance-team": {
        "industries": [
            "financial-services",
        ],
        "departments": [
            "finance",
        ],
        "max_classification": "internal",
    },
}


def _apply_policy(
    policy: dict,
    industries: set,
    departments: set,
    current_classification: str,
) -> str:
    industries.update(
        policy["industries"]
    )

    departments.update(
        policy["departments"]
    )

    policy_classification = (
        policy["max_classification"]
    )

    if (
        CLASSIFICATION_LEVELS[
            policy_classification
        ]
        >
        CLASSIFICATION_LEVELS[
            current_classification
        ]
    ):
        return policy_classification

    return current_classification


def build_authorization_context(
    identity: UserIdentity,
) -> AuthorizationContext:

    if not identity.authenticated:
        raise PermissionError(
            "User must be authenticated."
        )

    industries = set()
    departments = set()

    max_classification = "public"

    for role in identity.roles:
        policy = ROLE_ACCESS_POLICIES.get(
            role
        )

        if not policy:
            continue

        max_classification = _apply_policy(
            policy=policy,
            industries=industries,
            departments=departments,
            current_classification=max_classification,
        )

    for group in identity.groups:
        policy = GROUP_ACCESS_POLICIES.get(
            group
        )

        if not policy:
            continue

        max_classification = _apply_policy(
            policy=policy,
            industries=industries,
            departments=departments,
            current_classification=max_classification,
        )

    if not industries:
        raise PermissionError(
            "Authenticated user has no RAG access policy."
        )

    return AuthorizationContext(
        user_id=identity.user_id,
        roles=identity.roles.copy(),
        groups=identity.groups.copy(),
        allowed_industries=sorted(
            industries
        ),
        allowed_departments=sorted(
            departments
        ),
        max_classification=max_classification,
    )