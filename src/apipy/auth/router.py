import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from apipy.auth.models import (
    fake_credentials_db,
    ip_rate_limit_db,
    login_attempts_db,
    magic_tokens_db,
    refresh_tokens_db,
    security_events_db,
    token_blacklist,
)
from apipy.auth.schemas import (
    LoginRequest,
    MagicLinkConsumeRequest,
    MagicLinkRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPairResponse,
)
from apipy.auth.security import IP_RATE_LIMIT_ATTEMPTS, IP_RATE_LIMIT_WINDOW_SECONDS, decode_jwt
from apipy.auth.service import (
    consume_magic_link,
    create_magic_link,
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
)
from apipy.users.models import fake_db

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _assert_ip_rate_limit(ip: str):
    now = int(time.time())
    attempts = ip_rate_limit_db.setdefault(ip, [])
    attempts[:] = [ts for ts in attempts if ts > now - IP_RATE_LIMIT_WINDOW_SECONDS]
    if len(attempts) >= IP_RATE_LIMIT_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many requests from IP")
    attempts.append(now)


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    created_user = register_user(payload.name, payload.email, payload.password, fake_db, fake_credentials_db, security_events_db)
    if not created_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return created_user


@router.post("/login", response_model=TokenPairResponse)
def login(payload: LoginRequest, request: Request):
    _assert_ip_rate_limit(request.client.host if request.client else "unknown")
    login_result = login_user(
        payload.name,
        payload.password,
        fake_db,
        fake_credentials_db,
        refresh_tokens_db,
        login_attempts_db,
        security_events_db,
        payload.device_id,
    )
    if login_result and "error" in login_result:
        raise HTTPException(status_code=429, detail=login_result["error"])
    if not login_result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return login_result


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(payload: RefreshRequest):
    if payload.refresh_token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token revoked")
    refreshed = refresh_access_token(payload.refresh_token, refresh_tokens_db, security_events_db)
    if not refreshed:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return refreshed


@router.post("/logout")
def logout(payload: RefreshRequest):
    ok = logout_user(payload.refresh_token, refresh_tokens_db, token_blacklist, security_events_db, payload.session_id)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {"status": "logged out"}


@router.post("/magic-link/request")
def request_magic_link(payload: MagicLinkRequest):
    magic_link = create_magic_link(payload.email, fake_db, magic_tokens_db, security_events_db)
    if not magic_link:
        raise HTTPException(status_code=404, detail="User not found")
    return magic_link


@router.post("/magic-link/consume", response_model=TokenPairResponse)
def login_by_magic_link(payload: MagicLinkConsumeRequest):
    token_pair = consume_magic_link(payload.token, fake_db, refresh_tokens_db, magic_tokens_db, security_events_db)
    if not token_pair:
        raise HTTPException(status_code=401, detail="Invalid or expired magic link")
    return token_pair


@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    if token in token_blacklist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    payload = decode_jwt(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {
        "user_id": payload["user_id"],
        "name": payload["sub"],
        "scope": payload["scope"],
        "session_id": payload.get("session_id"),
        "device_id": payload.get("device_id"),
    }
