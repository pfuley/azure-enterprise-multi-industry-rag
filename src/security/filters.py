from src.security.authorization import AuthorizationContext


CLASSIFICATION_LEVELS = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3,
}


def escape_odata_value(
    value: str,
) -> str:
    return value.replace(
        "'",
        "''",
    )


def build_authorization_filter(
    auth: AuthorizationContext,
) -> str:

    filters = []

    # -----------------------------------------
    # 1. Industry access
    # -----------------------------------------

    if auth.allowed_industries:

        industries = ",".join(
            escape_odata_value(
                value
            )
            for value
            in auth.allowed_industries
        )

        filters.append(
            (
                "search.in("
                f"industry, '{industries}', ','"
                ")"
            )
        )

    # -----------------------------------------
    # 2. Department access
    # -----------------------------------------

    if auth.allowed_departments:

        departments = ",".join(
            escape_odata_value(
                value
            )
            for value
            in auth.allowed_departments
        )

        filters.append(
            (
                "search.in("
                f"department, '{departments}', ','"
                ")"
            )
        )

    # -----------------------------------------
    # 3. Classification access
    # -----------------------------------------

    max_level = (
        CLASSIFICATION_LEVELS.get(
            auth.max_classification
        )
    )

    if max_level is None:
        raise ValueError(
            "Unknown classification: "
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
        (
            "search.in("
            "classification, "
            f"'{classifications}', ','"
            ")"
        )
    )

    # -----------------------------------------
    # 4. Build document ACL conditions
    #
    # Access is granted when:
    #
    # - document has no group AND no role ACL
    #
    # OR
    #
    # - user's group matches allowed_groups
    #
    # OR
    #
    # - user's internal role matches
    #   allowed_roles
    #
    # This means a user does NOT need to match
    # both group and role simultaneously.
    # -----------------------------------------

    acl_conditions = [
        (
            "("
            "not allowed_groups/any() "
            "and "
            "not allowed_roles/any()"
            ")"
        )
    ]

    # -----------------------------------------
    # Group ACL
    # -----------------------------------------

    if auth.groups:

        groups = ",".join(
            escape_odata_value(
                value
            )
            for value
            in auth.groups
        )

        acl_conditions.append(
            (
                "allowed_groups/any("
                f"g: search.in(g, '{groups}', ',')"
                ")"
            )
        )

    # -----------------------------------------
    # Role ACL
    # -----------------------------------------

    if auth.roles:

        roles = ",".join(
            escape_odata_value(
                value
            )
            for value
            in auth.roles
        )

        acl_conditions.append(
            (
                "allowed_roles/any("
                f"r: search.in(r, '{roles}', ',')"
                ")"
            )
        )

    # -----------------------------------------
    # Combine ACL conditions using OR
    # -----------------------------------------

    acl_filter = (
        "("
        + " or ".join(
            acl_conditions
        )
        + ")"
    )

    filters.append(
        acl_filter
    )

    # -----------------------------------------
    # 5. Combine all authorization controls
    # -----------------------------------------

    return " and ".join(
        filters
    )