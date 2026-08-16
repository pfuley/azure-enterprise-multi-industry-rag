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
        "internal_role": "employee",
        "industries": [
            "it-support",
        ],
        "departments": [
            "service-desk",
        ],
        "max_classification": "internal",
    },

    "RAG.Admin": {
        "internal_role": "admin",
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
    """
    Apply one role/group access policy.

    Adds permitted industries and departments
    and returns the highest classification level
    granted by the policy.
    """

    industries.update(
        policy.get(
            "industries",
            [],
        )
    )

    departments.update(
        policy.get(
            "departments",
            [],
        )
    )

    policy_classification = policy.get(
        "max_classification",
        "public",
    )

    if policy_classification not in CLASSIFICATION_LEVELS:
        raise ValueError(
            "Unknown classification in access policy: "
            f"{policy_classification}"
        )

    if current_classification not in CLASSIFICATION_LEVELS:
        raise ValueError(
            "Unknown current classification: "
            f"{current_classification}"
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
    """
    Convert a validated UserIdentity into the
    application's AuthorizationContext.

    Microsoft Entra roles/groups are translated
    into internal RAG permissions here.
    """

    # -----------------------------------------
    # 1. Require authenticated identity
    # -----------------------------------------

    if not identity.authenticated:
        raise PermissionError(
            "User must be authenticated."
        )

    # -----------------------------------------
    # 2. Prepare accumulated permissions
    # -----------------------------------------

    industries = set()
    departments = set()
    internal_roles = set()

    max_classification = "public"

    # -----------------------------------------
    # 3. Apply Entra application-role policies
    #
    # Example:
    #
    # RAG.Employee
    #       ↓
    # internal role = employee
    # industry      = it-support
    # department    = service-desk
    # classification = internal
    # -----------------------------------------

    for role in identity.roles:

        policy = ROLE_ACCESS_POLICIES.get(
            role
        )

        if not policy:
            continue

        internal_role = policy.get(
            "internal_role"
        )

        if internal_role:
            internal_roles.add(
                internal_role
            )

        max_classification = _apply_policy(
            policy=policy,
            industries=industries,
            departments=departments,
            current_classification=(
                max_classification
            ),
        )

    # -----------------------------------------
    # 4. Apply Entra group policies
    #
    # These currently use friendly development
    # group names.
    #
    # Later, real Entra group object IDs can be
    # mapped here instead.
    # -----------------------------------------

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
            current_classification=(
                max_classification
            ),
        )

    # -----------------------------------------
    # 5. Fail closed
    #
    # An authenticated user without a recognized
    # role/group should not receive default RAG
    # access.
    # -----------------------------------------

    if not industries:
        raise PermissionError(
            "Authenticated user has no RAG access policy."
        )

    # -----------------------------------------
    # 6. Build internal authorization context
    #
    # Notice:
    #
    # identity.roles
    #     contains Entra roles such as:
    #     RAG.Employee
    #
    # AuthorizationContext.roles
    #     contains internal ACL roles such as:
    #     employee
    #
    # This translation is intentional.
    # -----------------------------------------

    return AuthorizationContext(
        user_id=identity.user_id,

        roles=sorted(
            internal_roles
        ),

        groups=identity.groups.copy(),

        allowed_industries=sorted(
            industries
        ),

        allowed_departments=sorted(
            departments
        ),

        max_classification=(
            max_classification
        ),
    )