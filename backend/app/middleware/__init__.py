import logging

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from jose.constants import Algorithms
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models import User, UserRole

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

_jwks: dict | None = None


async def get_jwks() -> dict:
    global _jwks
    if _jwks is not None:
        return _jwks

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.oidc_issuer}/.well-known/openid-configuration"
        )
        resp.raise_for_status()
        config = resp.json()
        jwks_uri = config["jwks_uri"]
        resp = await client.get(jwks_uri)
        resp.raise_for_status()
        _jwks = resp.json()
        return _jwks


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = credentials.credentials

    try:
        jwks = await get_jwks()
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwk
                break

        if key is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        payload = jwt.decode(
            token,
            key,
            algorithms=[Algorithms.RS256],
            options={"verify_exp": True, "verify_aud": False},
        )

        oidc_sub = payload.get("sub")
        if oidc_sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    except (JWTError, httpx.HTTPError) as e:
        logger.warning("JWT validation failed: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    result = await db.execute(select(User).where(User.oidc_sub == oidc_sub))
    user = result.scalar_one_or_none()

    if user is None:
        preferred_username = payload.get("preferred_username", oidc_sub)
        email = payload.get("email")
        display_name = payload.get("name", preferred_username)

        user = User(
            oidc_sub=oidc_sub,
            username=preferred_username,
            email=email,
            display_name=display_name,
            role=UserRole.user,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user