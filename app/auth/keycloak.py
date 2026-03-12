"""Keycloak JWT bearer authentication for FastAPI.

Validates tokens issued by a specific Keycloak realm. The JWKS keys are fetched
once at startup and cached for the lifetime of the application. They are
refreshed automatically when an unknown key ID (kid) is encountered.
"""

import logging
import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode

from app.config import settings

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=True)

# Simple in-process JWKS cache: {kid: key_data}
_jwks_cache: dict[str, Any] = {}
_jwks_fetched_at: float = 0.0
_JWKS_TTL = 3600  # re-fetch JWKS after 1 hour


async def _fetch_jwks() -> dict[str, Any]:
    """Fetch the JWKS from Keycloak and return a {kid: key} mapping."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(settings.keycloak_jwks_uri, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    return {key["kid"]: key for key in data.get("keys", [])}


async def _get_jwks(force_refresh: bool = False) -> dict[str, Any]:
    global _jwks_cache, _jwks_fetched_at
    now = time.monotonic()
    if force_refresh or not _jwks_cache or (now - _jwks_fetched_at) > _JWKS_TTL:
        _jwks_cache = await _fetch_jwks()
        _jwks_fetched_at = now
    return _jwks_cache


def _decode_token(token: str, key_data: Any) -> dict[str, Any]:
    public_key = jwk.construct(key_data)
    options = {
        "verify_exp": True,
        "verify_aud": bool(settings.keycloak_client_id),
    }
    audience = settings.keycloak_client_id if settings.keycloak_client_id else None
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=audience,
        issuer=settings.keycloak_issuer,
        options=options,
    )


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """Dependency that validates a Keycloak JWT and returns the decoded payload."""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract kid from header without full verification first
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
    except JWTError:
        raise credentials_exception

    if not kid:
        raise credentials_exception

    jwks = await _get_jwks()
    key_data = jwks.get(kid)

    if key_data is None:
        # Unknown kid — try a forced refresh once (key rotation)
        jwks = await _get_jwks(force_refresh=True)
        key_data = jwks.get(kid)

    if key_data is None:
        raise credentials_exception

    try:
        payload = _decode_token(token, key_data)
    except JWTError as exc:
        logger.debug("JWT validation failed: %s", exc)
        raise credentials_exception

    return payload


# Re-export as a dependency alias used throughout routers
require_auth = Depends(get_current_token)
