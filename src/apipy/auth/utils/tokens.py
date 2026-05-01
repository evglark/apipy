import uuid

from apipy.auth.security import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    REFRESH_TOKEN_EXPIRE_SECONDS,
    create_jwt,
    new_session_id,
)
from apipy.users.models import User


def _issue_token_pair(
    user: User, device_id: str, permissions: list[str], session_id: str | None = None
):
    session_id = session_id or new_session_id()
    effective_device_id = device_id
    access_claims = {
        "sub": user.name,
        "user_id": user.id,
        "scope": user.role,
        "role": user.role,
        "permissions": permissions,
        "type": "access",
        "session_id": session_id,
        "device_id": effective_device_id,
    }
    refresh_jti = str(uuid.uuid4())
    refresh_claims = {
        "sub": user.name,
        "user_id": user.id,
        "scope": "refresh",
        "role": user.role,
        "permissions": permissions,
        "type": "refresh",
        "jti": refresh_jti,
        "session_id": session_id,
        "device_id": effective_device_id,
    }
    return {
        "access_token": create_jwt(access_claims, ACCESS_TOKEN_EXPIRE_SECONDS),
        "refresh_token": create_jwt(refresh_claims, REFRESH_TOKEN_EXPIRE_SECONDS),
        "token_type": "bearer",
        "session_id": session_id,
        "refresh_jti": refresh_jti,
        "device_id": effective_device_id,
    }
