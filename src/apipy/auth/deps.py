from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from apipy.auth.security import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def require_roles(*allowed_roles: str):
    async def _require(token: str = Depends(oauth2_scheme)):
        payload = decode_jwt(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        role = payload.get("role")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient scope",
            )
        return payload

    return _require
