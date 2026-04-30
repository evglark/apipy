from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from apipy.auth.models import (
    fake_credentials_db,
    login_attempts_db,
    refresh_tokens_db,
    token_blacklist,
)
from apipy.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPairResponse,
)
from apipy.auth.security import decode_jwt
from apipy.auth.service import login_user, logout_user, refresh_access_token, register_user
from apipy.users.models import fake_db

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    created_user = register_user(payload.name, payload.password, fake_db, fake_credentials_db)
    if not created_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return created_user


@router.post("/login", response_model=TokenPairResponse)
def login(payload: LoginRequest):
    login_result = login_user(
        payload.name,
        payload.password,
        fake_db,
        fake_credentials_db,
        refresh_tokens_db,
        login_attempts_db,
    )
    if login_result and "error" in login_result:
        raise HTTPException(status_code=429, detail=login_result["error"])
    if not login_result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return login_result


@router.post("/refresh")
def refresh(payload: RefreshRequest):
    if payload.refresh_token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token revoked")
    refreshed = refresh_access_token(payload.refresh_token, refresh_tokens_db)
    if not refreshed:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return refreshed


@router.post("/logout")
def logout(payload: RefreshRequest):
    ok = logout_user(payload.refresh_token, refresh_tokens_db, token_blacklist)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {"status": "logged out"}


@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    if token in token_blacklist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    payload = decode_jwt(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {"user_id": payload["user_id"], "name": payload["sub"], "scope": payload["scope"]}
