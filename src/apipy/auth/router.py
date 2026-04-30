import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from apipy.database import get_db
from apipy.auth.models import BlacklistedToken, IPRateLimit
from apipy.auth.schemas import (
    LoginRequest,
    MagicLinkConsumeRequest,
    MagicLinkRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPairResponse,
)
from apipy.auth.security import (
    IP_RATE_LIMIT_ATTEMPTS,
    IP_RATE_LIMIT_WINDOW_SECONDS,
    decode_jwt,
)
from apipy.auth.service import (
    consume_magic_link,
    create_magic_link,
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def _assert_ip_rate_limit(ip: str, db: AsyncSession):
    now = int(time.time())
    result = await db.execute(select(IPRateLimit).where(IPRateLimit.ip == ip))
    record = result.scalar_one_or_none()

    if not record:
        record = IPRateLimit(ip=ip, attempts=str(now))
        db.add(record)
    else:
        attempts = [int(ts) for ts in record.attempts.split(",") if ts]
        attempts = [ts for ts in attempts if ts > now - IP_RATE_LIMIT_WINDOW_SECONDS]
        if len(attempts) >= IP_RATE_LIMIT_ATTEMPTS:
            await db.commit()
            raise HTTPException(status_code=429, detail="Too many requests from IP")
        attempts.append(now)
        record.attempts = ",".join(map(str, attempts))

    await db.commit()


@router.post("/register", response_model=RegisterResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    created_user = await register_user(
        payload.name, payload.email, payload.password, db
    )
    if not created_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return created_user


@router.post("/login", response_model=TokenPairResponse)
async def login(
    payload: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    await _assert_ip_rate_limit(
        request.client.host if request.client else "unknown", db
    )
    login_result = await login_user(
        payload.name,
        payload.password,
        db,
        payload.device_id,
    )
    if login_result and "error" in login_result:
        raise HTTPException(status_code=429, detail=login_result["error"])
    if not login_result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return login_result


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    # Check blacklist
    result = await db.execute(
        select(BlacklistedToken).where(BlacklistedToken.token == payload.refresh_token)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=401, detail="Token revoked")

    refreshed = await refresh_access_token(payload.refresh_token, db)
    if not refreshed:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return refreshed


@router.post("/logout")
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    ok = await logout_user(payload.refresh_token, db, payload.session_id)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {"status": "logged out"}


@router.post("/magic-link/request")
async def request_magic_link(
    payload: MagicLinkRequest, db: AsyncSession = Depends(get_db)
):
    magic_link = await create_magic_link(payload.email, db)
    if not magic_link:
        raise HTTPException(status_code=404, detail="User not found")
    return magic_link


@router.post("/magic-link/consume", response_model=TokenPairResponse)
async def login_by_magic_link(
    payload: MagicLinkConsumeRequest, db: AsyncSession = Depends(get_db)
):
    token_pair = await consume_magic_link(payload.token, db)
    if not token_pair:
        raise HTTPException(status_code=401, detail="Invalid or expired magic link")
    return token_pair


@router.get("/me")
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    # Check blacklist
    result = await db.execute(
        select(BlacklistedToken).where(BlacklistedToken.token == token)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
        )

    payload = decode_jwt(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return {
        "user_id": payload["user_id"],
        "name": payload["sub"],
        "scope": payload["scope"],
        "session_id": payload.get("session_id"),
        "device_id": payload.get("device_id"),
    }
