import time
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from apipy.auth.models import BlacklistedToken, Credential, Device, LoginAttempt, RefreshToken
from apipy.auth.security import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    LOGIN_BLOCK_SECONDS,
    MAX_LOGIN_ATTEMPTS,
    REFRESH_TOKEN_EXPIRE_SECONDS,
    create_jwt,
    decode_jwt,
    hash_token,
    verify_password,
)
from apipy.auth.utils.events import _log_event
from apipy.auth.utils.queries import _find_user_by_email, _get_role_permissions
from apipy.auth.utils.tokens import _issue_token_pair


async def _is_blocked(email: str, db: AsyncSession):
    result = await db.execute(select(LoginAttempt).where(LoginAttempt.username == email))
    record = result.scalar_one_or_none()
    if not record:
        return False
    return record.blocked_until > int(time.time())


async def _register_failed_attempt(email: str, db: AsyncSession):
    now = int(time.time())
    result = await db.execute(select(LoginAttempt).where(LoginAttempt.username == email))
    record = result.scalar_one_or_none()
    if not record:
        record = LoginAttempt(username=email, count=1)
        record.created_at = now
        record.expires_at = now + LOGIN_BLOCK_SECONDS
        db.add(record)
    else:
        record.count += 1
        record.expires_at = now + LOGIN_BLOCK_SECONDS
        if record.count >= MAX_LOGIN_ATTEMPTS:
            record.blocked_until = now + LOGIN_BLOCK_SECONDS
    await db.commit()


async def _reset_failed_attempts(email: str, db: AsyncSession):
    await db.execute(delete(LoginAttempt).where(LoginAttempt.username == email))
    await db.commit()


async def login_user(
    email: str,
    password: str,
    db: AsyncSession,
    user_agent: str | None = None,
    ip: str | None = None,
):
    if await _is_blocked(email, db):
        await _log_event(db, "login_blocked", email=email)
        await db.commit()
        return {"error": "Too many login attempts. Try again later."}

    user = await _find_user_by_email(email, db)
    if not user:
        await _register_failed_attempt(email, db)
        await _log_event(db, "login_failed", email=email, reason="user_not_found")
        await db.commit()
        return None
    if not user.email_verified:
        await _log_event(db, "login_failed", email=email, reason="email_not_verified")
        await db.commit()
        return {"error": "Email is not verified", "status_code": 403}

    result = await db.execute(select(Credential).where(Credential.user_id == user.id))
    credentials = result.scalars().all()

    for cred in credentials:
        if verify_password(password, cred.password_hash):
            await _reset_failed_attempts(email, db)
            new_device = Device(
                user_id=user.id,
                user_agent=user_agent or "unknown",
                ip=ip,
                created_at=int(time.time()),
            )
            db.add(new_device)
            await db.flush()

            permissions = await _get_role_permissions(user.role, db)
            token_pair = _issue_token_pair(user, str(new_device.id), permissions)

            new_refresh = RefreshToken(
                jti=token_pair["refresh_jti"],
                user_id=user.id,
                revoked=False,
                session_id=token_pair["session_id"],
                device_id=str(new_device.id),
                created_at=int(time.time()),
                expires_at=int(time.time()) + REFRESH_TOKEN_EXPIRE_SECONDS,
            )
            db.add(new_refresh)
            await _log_event(
                db,
                "login_success",
                user_id=user.id,
                session_id=token_pair["session_id"],
            )
            await db.commit()
            return {k: v for k, v in token_pair.items() if k != "refresh_jti"}

    await _register_failed_attempt(email, db)
    await _log_event(db, "login_failed", email=email, reason="bad_password")
    await db.commit()
    return None


async def refresh_access_token(refresh_token: str, db: AsyncSession):
    payload = decode_jwt(refresh_token)
    if not payload or payload.get("type") != "refresh":
        await _log_event(db, "refresh_failed", reason="invalid_token")
        await db.commit()
        return None

    jti = payload.get("jti")
    result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    token_record = result.scalar_one_or_none()

    if not token_record:
        await _log_event(db, "refresh_failed", reason="revoked_or_missing", jti=jti)
        await db.commit()
        return None
    if token_record.revoked:
        token_record.reuse_detected = True
        session_id = token_record.session_id
        session_result = await db.execute(
            select(RefreshToken).where(RefreshToken.session_id == session_id)
        )
        session_tokens = session_result.scalars().all()
        for session_token in session_tokens:
            session_token.revoked = True
        await _log_event(
            db,
            "refresh_token_reuse_detected",
            user_id=token_record.user_id,
            session_id=session_id,
        )
        await db.commit()
        return None

    token_record.revoked = True
    new_jti = str(uuid.uuid4())

    new_refresh = RefreshToken(
        jti=new_jti,
        user_id=payload["user_id"],
        revoked=False,
        session_id=payload.get("session_id"),
        device_id=payload.get("device_id") or "unknown",
        created_at=int(time.time()),
        expires_at=int(time.time()) + REFRESH_TOKEN_EXPIRE_SECONDS,
    )
    db.add(new_refresh)

    access_claims = {
        "sub": payload["sub"],
        "user_id": payload["user_id"],
        "scope": payload.get("role", "user"),
        "role": payload.get("role", "user"),
        "permissions": payload.get("permissions", []),
        "type": "access",
        "session_id": payload.get("session_id", ""),
        "device_id": payload.get("device_id", "unknown"),
    }
    new_refresh_claims = {
        "sub": payload["sub"],
        "user_id": payload["user_id"],
        "scope": "refresh",
        "role": payload.get("role", "user"),
        "permissions": payload.get("permissions", []),
        "type": "refresh",
        "jti": new_jti,
        "session_id": payload.get("session_id", ""),
        "device_id": payload.get("device_id", "unknown"),
    }
    await _log_event(
        db, "refresh_rotated", user_id=payload["user_id"], old_jti=jti, new_jti=new_jti
    )
    await db.commit()

    return {
        "access_token": create_jwt(access_claims, ACCESS_TOKEN_EXPIRE_SECONDS),
        "refresh_token": create_jwt(new_refresh_claims, REFRESH_TOKEN_EXPIRE_SECONDS),
        "token_type": "bearer",
        "session_id": payload.get("session_id", ""),
    }


async def logout_user(
    refresh_token: str, db: AsyncSession, session_id: str | None = None
):
    payload = decode_jwt(refresh_token)
    if not payload or payload.get("type") != "refresh":
        await _log_event(db, "logout_failed", reason="invalid_token")
        await db.commit()
        return False

    db.add(BlacklistedToken(token=hash_token(refresh_token)))

    if session_id:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.session_id == session_id)
        )
        records = result.scalars().all()
        for rec in records:
            rec.revoked = True
        await _log_event(
            db,
            "logout_session_success",
            user_id=payload.get("user_id"),
            session_id=session_id,
        )
        await db.commit()
        return True

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.jti == payload.get("jti"))
    )
    token_record = result.scalar_one_or_none()
    if token_record:
        token_record.revoked = True
        await _log_event(
            db, "logout_success", user_id=payload.get("user_id"), jti=token_record.jti
        )
        await db.commit()
        return True

    await db.commit()
    return False
