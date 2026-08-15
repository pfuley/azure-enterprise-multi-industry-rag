import jwt
import requests

from jwt.algorithms import RSAAlgorithm

from src.core.config import (
    AZURE_ENTRA_API_CLIENT_ID,
    AZURE_ENTRA_TENANT_ID,
)
from src.security.identity import UserIdentity


def _get_openid_configuration() -> dict:
    if not AZURE_ENTRA_TENANT_ID:
        raise ValueError(
            "AZURE_ENTRA_TENANT_ID is not configured"
        )

    url = (
        "https://login.microsoftonline.com/"
        f"{AZURE_ENTRA_TENANT_ID}"
        "/v2.0/.well-known/openid-configuration"
    )

    response = requests.get(
        url,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def _get_signing_key(
    token: str,
    jwks_uri: str,
):
    headers = jwt.get_unverified_header(
        token
    )

    key_id = headers.get("kid")

    if not key_id:
        raise ValueError(
            "Token does not contain a key ID"
        )

    response = requests.get(
        jwks_uri,
        timeout=10,
    )

    response.raise_for_status()

    jwks = response.json()

    for key in jwks["keys"]:
        if key["kid"] == key_id:
            return RSAAlgorithm.from_jwk(
                key
            )

    raise ValueError(
        "Unable to find matching Entra signing key"
    )


def validate_access_token(
    token: str,
) -> UserIdentity:
    if not token:
        raise PermissionError(
            "Access token is required"
        )

    if not AZURE_ENTRA_API_CLIENT_ID:
        raise ValueError(
            "AZURE_ENTRA_CLIENT_ID is not configured"
        )

    configuration = (
        _get_openid_configuration()
    )

    signing_key = _get_signing_key(
        token=token,
        jwks_uri=configuration["jwks_uri"],
    )

    issuer = configuration["issuer"]

    expected_audiences = [
        AZURE_ENTRA_API_CLIENT_ID,
        f"api://{AZURE_ENTRA_API_CLIENT_ID}",
    ]

    last_error = None
    claims = None

    for audience in expected_audiences:
        try:
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=audience,
                issuer=issuer,
            )

            break

        except jwt.InvalidAudienceError as error:
            last_error = error

    if claims is None:
        raise PermissionError(
            "Token audience is not valid"
        ) from last_error

    user_id = claims.get("oid")

    if not user_id:
        raise PermissionError(
            "Token does not contain a user object ID"
        )

    roles = claims.get(
        "roles",
        [],
    )

    groups = claims.get(
        "groups",
        [],
    )

    return UserIdentity(
        user_id=user_id,
        display_name=claims.get("name"),
        email=(
            claims.get("preferred_username")
            or claims.get("email")
        ),
        roles=roles,
        groups=groups,
        authenticated=True,
    )