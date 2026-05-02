from collections.abc import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from apipy.auth.utils.security import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_jwt(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload


def require_role(role: str) -> Callable:
    async def wrapper(payload: dict = Depends(get_current_user)):
        if payload.get("role") != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return payload

    return wrapper


def require_roles(*allowed_roles: str) -> Callable:
    async def wrapper(payload: dict = Depends(get_current_user)):
        if payload.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return payload

    return wrapper


def require_permission(permission: str) -> Callable:
    async def wrapper(payload: dict = Depends(get_current_user)):
        if permission not in payload.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing permission",
            )
        return payload

    return wrapper
