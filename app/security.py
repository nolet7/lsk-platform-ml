"""OIDC access-token verification; demo-key authorization is forbidden in production."""
import os
from functools import lru_cache

from fastapi import Header, HTTPException
import jwt
from jwt import PyJWKClient

@lru_cache(maxsize=8)
def jwks_client(url: str):
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300)

def auth(authorization: str | None = Header(default=None),
         x_demo_key: str | None = Header(default=None)):
    env = os.getenv("APP_ENV", "local")
    if env != "production":
        if x_demo_key != os.getenv("DEMO_API_KEY", "local-demo-key"):
            raise HTTPException(401, "invalid demo key")
        return {"sub": "local-demo", "scope": "ml:read ml:predict ml:review"}

    issuer = os.getenv("OIDC_ISSUER", "").rstrip("/")
    audience = os.getenv("OIDC_AUDIENCE", "")
    jwks_url = os.getenv("OIDC_JWKS_URL", "")
    if not (issuer.startswith("https://") and audience and jwks_url.startswith("https://")):
        raise HTTPException(503, "production OIDC configuration missing")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer token required")
    token = authorization[7:]
    try:
        signing_key = jwks_client(jwks_url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key=signing_key, algorithms=["RS256"],
                            audience=audience, issuer=issuer,
                            options={"require": ["exp", "iat", "sub", "iss", "aud"]})
    except (jwt.PyJWTError, ValueError, TimeoutError) as exc:
        raise HTTPException(401, "invalid access token") from exc
    if not claims.get("sub"):
        raise HTTPException(401, "subject required")
    return claims

def require_scope(claims: dict, scope: str):
    scopes = set(str(claims.get("scope", "")).split())
    # Some providers use permissions array rather than OAuth scope string.
    permissions = claims.get("permissions", [])
    if isinstance(permissions, list):
        scopes.update(x for x in permissions if isinstance(x, str))
    if scope not in scopes:
        raise HTTPException(403, "missing required permission")
