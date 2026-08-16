import jwt
import requests

from jwt.algorithms import RSAAlgorithm

from src.core.config import (
    AZURE_ENTRA_API_CLIENT_ID,
    AZURE_ENTRA_TENANT_ID,
)
from src.security.identity import UserIdentity


REQUIRED_SCOPE = "RAG.Access"


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
    # -----------------------------------------
    # 1. Read JWT header without trusting
    #    the token yet
    # -----------------------------------------

    headers = jwt.get_unverified_header(
        token
    )

    key_id = headers.get(
        "kid"
    )

    if not key_id:
        raise PermissionError(
            "Token does not contain a key ID."
        )

    # -----------------------------------------
    # 2. Download Microsoft Entra signing keys
    # -----------------------------------------

    response = requests.get(
        jwks_uri,
        timeout=10,
    )

    response.raise_for_status()

    jwks = response.json()

    # -----------------------------------------
    # 3. Find the public signing key matching
    #    the token's kid
    # -----------------------------------------

    for key in jwks.get(
        "keys",
        [],
    ):
        if key.get(
            "kid"
        ) == key_id:

            return RSAAlgorithm.from_jwk(
                key
            )

    raise PermissionError(
        "Unable to find a matching "
        "Microsoft Entra signing key."
    )


def validate_access_token(
    token: str,
) -> UserIdentity:
    """
    Validate a Microsoft Entra access token and
    convert trusted claims into UserIdentity.

    Validation includes:
    - cryptographic signature
    - issuer
    - audience
    - expiration
    - required delegated scope
    - user object ID
    """

    # -----------------------------------------
    # 1. Require token
    # -----------------------------------------

    if not token:
        raise PermissionError(
            "Access token is required."
        )

    if not AZURE_ENTRA_API_CLIENT_ID:
        raise ValueError(
            "AZURE_ENTRA_API_CLIENT_ID "
            "is not configured"
        )

    # -----------------------------------------
    # 2. Load Microsoft Entra metadata
    # -----------------------------------------

    configuration = (
        _get_openid_configuration()
    )

    jwks_uri = configuration[
        "jwks_uri"
    ]

    issuer = configuration[
        "issuer"
    ]

    # -----------------------------------------
    # 3. Find the correct Microsoft signing key
    # -----------------------------------------

    signing_key = _get_signing_key(
        token=token,
        jwks_uri=jwks_uri,
    )

    # -----------------------------------------
    # 4. Define audiences accepted by our API
    #
    # Depending on token/resource configuration,
    # the aud claim can use either representation.
    # -----------------------------------------

    expected_audiences = [
        AZURE_ENTRA_API_CLIENT_ID,
        (
            f"api://"
            f"{AZURE_ENTRA_API_CLIENT_ID}"
        ),
    ]

    claims = None
    last_error = None

    # -----------------------------------------
    # 5. Cryptographically validate JWT
    #
    # jwt.decode() also validates expiration
    # by default when the exp claim exists.
    # -----------------------------------------

    for audience in expected_audiences:

        try:

            claims = jwt.decode(
                token,
                signing_key,
                algorithms=[
                    "RS256"
                ],
                audience=audience,
                issuer=issuer,
            )

            break

        except jwt.InvalidAudienceError as error:

            last_error = error

    if claims is None:
        raise PermissionError(
            "Token audience is not valid."
        ) from last_error

    # -----------------------------------------
    # 6. Validate tenant explicitly
    # -----------------------------------------

    token_tenant_id = claims.get(
        "tid"
    )

    if (
        not token_tenant_id
        or token_tenant_id
        != AZURE_ENTRA_TENANT_ID
    ):
        raise PermissionError(
            "Token tenant is not valid."
        )

    # -----------------------------------------
    # 7. Require delegated API scope
    #
    # Example:
    #
    # scp = "RAG.Access"
    #
    # Multiple delegated scopes are returned as
    # one space-separated string.
    # -----------------------------------------

    scope_claim = claims.get(
        "scp",
        "",
    )

    granted_scopes = (
        scope_claim.split()
    )

    if REQUIRED_SCOPE not in granted_scopes:
        raise PermissionError(
            "Access token does not contain "
            f"the required {REQUIRED_SCOPE} scope."
        )

    # -----------------------------------------
    # 8. Require stable Entra user identity
    # -----------------------------------------

    user_id = claims.get(
        "oid"
    )

    if not user_id:
        raise PermissionError(
            "Token does not contain a "
            "user object ID."
        )

    # -----------------------------------------
    # 9. Read trusted app roles
    # -----------------------------------------

    roles = claims.get(
        "roles",
        [],
    )

    if not isinstance(
        roles,
        list,
    ):
        roles = []

    # -----------------------------------------
    # 10. Read trusted Entra group claims
    #
    # These may be empty if group claims have
    # not been configured in the app registration.
    # -----------------------------------------

    groups = claims.get(
        "groups",
        [],
    )

    if not isinstance(
        groups,
        list,
    ):
        groups = []

    # -----------------------------------------
    # 11. Resolve basic identity information
    # -----------------------------------------

    display_name = claims.get(
        "name"
    )

    email = (
        claims.get(
            "preferred_username"
        )
        or claims.get(
            "email"
        )
        or claims.get(
            "upn"
        )
    )

    # -----------------------------------------
    # 12. Return trusted application identity
    # -----------------------------------------

    return UserIdentity(
        user_id=user_id,
        display_name=display_name,
        email=email,
        roles=roles,
        groups=groups,
        authenticated=True,
    )