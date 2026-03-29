from fastapi import APIRouter, HTTPException

from apipy.models.auth import AuthLoginRequest, AuthRegisterRequest, AuthResponse
from apipy.services.auth_service import (
    auth_sessions_db,
    auth_users_db,
    get_auth_user_by_username,
    login_user,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def auth_register(payload: AuthRegisterRequest):
    """Регистрируем нового пользователя.

    Важно: это отдельный контур от CRUD /users, чтобы на обучении
    разделить домены "данные пользователя" и "безопасность/логин".
    """

    existing_user = get_auth_user_by_username(payload.username, auth_users_db)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    created_user = register_user(
        username=payload.username,
        password=payload.password,
        db=auth_users_db,
    )
    return {
        "status": "registered",
        "user": created_user,
    }


@router.post("/login", response_model=AuthResponse)
def auth_login(payload: AuthLoginRequest):
    """Логиним пользователя и выдаем токен."""

    auth_result = login_user(
        username=payload.username,
        password=payload.password,
        users_db=auth_users_db,
        sessions_db=auth_sessions_db,
    )
    if not auth_result:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "access_token": auth_result["access_token"],
        "user_id": auth_result["user_id"],
    }
