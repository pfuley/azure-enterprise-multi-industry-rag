from fastapi import Header, HTTPException, status

from src.security.access_policy import (
    build_authorization_context,
)
from src.security.authorization import (
    AuthorizationContext,
)
from src.security.token_validator import (
    validate_access_token,
)


def get_authorization_context(
    authorization: str | None = Header(
        default=None
    ),
) -> AuthorizationContext:

    # -----------------------------------------
    # 1. Require Authorization header
    # -----------------------------------------

    if not authorization:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Authorization header is required."
            ),
        )

    # -----------------------------------------
    # 2. Require Bearer authentication
    # -----------------------------------------

    scheme, _, token = (
        authorization.partition(" ")
    )

    if (
        scheme.lower() != "bearer"
        or not token
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "A valid Bearer token is required."
            ),
        )

    # -----------------------------------------
    # 3. Validate Microsoft Entra token
    # -----------------------------------------

    try:
        identity = validate_access_token(
            token
        )

    except Exception:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Access token validation failed."
            ),
        )

    # -----------------------------------------
    # 4. Convert identity to application
    #    authorization permissions
    # -----------------------------------------

    try:
        return build_authorization_context(
            identity
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(error),
        )