from src.security.authorization import AuthorizationContext


CLASSIFICATION_LEVELS = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3,
}


def escape_odata_value(value: str) -> str:
    return value.replace("'", "''")


def build_authorization_filter(
    auth: AuthorizationContext,
) -> str:
    filters = []

    # -----------------------------------------
    # Industry permissions
    # -----------------------------------------

    if auth.allowed_industries:
        industries = ",".join(
            escape_odata_value(value)
            for value in auth.allowed_industries
        )

        filters.append(
            f"search.in(industry, '{industries}', ',')"
        )

    # -----------------------------------------
    # Department permissions
    # -----------------------------------------

    if auth.allowed_departments:
        departments = ",".join(
            escape_odata_value(value)
            for value in auth.allowed_departments
        )

        filters.append(
            f"search.in(department, '{departments}', ',')"
        )

    # -----------------------------------------
    # Group ACLs
    # -----------------------------------------

    if auth.groups:
        groups = ",".join(
            escape_odata_value(value)
            for value in auth.groups
        )

        filters.append(
            "("
            "not allowed_groups/any() "
            "or "
            "allowed_groups/any("
            f"g: search.in(g, '{groups}', ',')"
            ")"
            ")"
        )
    else:
        filters.append(
            "not allowed_groups/any()"
        )   

    # -----------------------------------------
    # Role ACLs
    # -----------------------------------------

    if auth.roles:
        roles = ",".join(
            escape_odata_value(value)
            for value in auth.roles
        )

        filters.append(
            "("
            "not allowed_roles/any() "
            "or "
            "allowed_roles/any("
            f"r: search.in(r, '{roles}', ',')"
            ")"
            ")"
        )
    else:
        filters.append(
            "not allowed_roles/any()"
        )

    # -----------------------------------------
    # Classification access
    # -----------------------------------------

    max_level = CLASSIFICATION_LEVELS.get(
        auth.max_classification
    )

    if max_level is None:
        raise ValueError(
            f"Unknown classification: "
            f"{auth.max_classification}"
        )

    allowed_classifications = [
        classification
        for classification, level
        in CLASSIFICATION_LEVELS.items()
        if level <= max_level
    ]

    classifications = ",".join(
        allowed_classifications
    )

    filters.append(
        f"search.in(classification, "
        f"'{classifications}', ',')"
    )

    if not filters:
        return ""

    return " and ".join(filters)