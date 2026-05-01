import time
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from apipy.auth.security import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    LOGIN_BLOCK_SECONDS,
    MAX_LOGIN_ATTEMPTS,
    REFRESH_TOKEN_EXPIRE_SECONDS,
    create_jwt,
    decode_jwt,
    hash_password,
    new_session_id,
    verify_password,
)
from apipy.users.models import User
from apipy.auth.models import (
    Credential,
    RefreshToken,
    BlacklistedToken,
    LoginAttempt,
    SecurityEvent,
    MagicToken,
)


async def _log_event(
    db: AsyncSession, event: str, user_id: int | None = None, **details
):
    new_event = SecurityEvent(
        event=event, ts=int(time.time()), user_id=user_id, details=str(details)
    )
    db.add(new_event)
    # We don't necessarily need to commit here if we commit at the end of service call


async def _find_user_by_name(name: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.name == name))
    return result.scalar_one_or_none()


async def _find_user_by_email(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def _issue_token_pair(
    user: User, device_id: str | None = None, session_id: str | None = None
):
    session_id = session_id or new_session_id()
    effective_device_id = device_id or "unknown"
    access_claims = {
        "sub": user.name,
        "user_id": user.id,
        "scope": "access",
        "type": "access",
        "session_id": session_id,
        "device_id": effective_device_id,
    }
    refresh_jti = str(uuid.uuid4())
    refresh_claims = {
        "sub": user.name,
        "user_id": user.id,
        "scope": "refresh",
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
    }


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
    device_id: str | None = None,
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

    result = await db.execute(select(Credential).where(Credential.user_id == user.id))
    credentials = result.scalars().all()

    for cred in credentials:
        if verify_password(password, cred.password_hash):
            await _reset_failed_attempts(email, db)
            token_pair = _issue_token_pair(user, device_id)

            new_refresh = RefreshToken(
                jti=token_pair["refresh_jti"],
                user_id=user.id,
                revoked=False,
                session_id=token_pair["session_id"],
                device_id=device_id or "unknown",
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
        "scope": "access",
        "type": "access",
        "session_id": payload.get("session_id", ""),
        "device_id": payload.get("device_id", "unknown"),
    }
    new_refresh_claims = {
        "sub": payload["sub"],
        "user_id": payload["user_id"],
        "scope": "refresh",
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

    db.add(BlacklistedToken(token=refresh_token))

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


async def register_user(name: str, email: str, password: str, db: AsyncSession):
    user = await _find_user_by_name(name, db) or await _find_user_by_email(email, db)
    if user:
        await _log_event(db, "register_failed", username=name, reason="exists")
        await db.commit()
        return None

    new_user = User(name=name, email=email)
    db.add(new_user)
    await db.flush()  # Get ID

    new_cred = Credential(user_id=new_user.id, password_hash=hash_password(password))
    db.add(new_cred)

    await _log_event(db, "register_success", user_id=new_user.id)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def create_magic_link(email: str, db: AsyncSession, ttl_seconds: int = 600):
    user = await _find_user_by_email(email, db)
    if not user:
        await _log_event(
            db, "magic_link_request_failed", email=email, reason="user_not_found"
        )
        await db.commit()
        return None
    token = str(uuid.uuid4())
    new_magic = MagicToken(
        token=token, user_id=user.id, exp=int(time.time()) + ttl_seconds, used=False
    )
    db.add(new_magic)
    await _log_event(db, "magic_link_created", user_id=user.id)
    await db.commit()
    return {"token": token, "login_link": f"/auth/magic-link/consume?token={token}"}


async def consume_magic_link(token: str, db: AsyncSession):
    now = int(time.time())
    result = await db.execute(select(MagicToken).where(MagicToken.token == token))
    record = result.scalar_one_or_none()

    if not record or record.used or record.exp < now:
        await _log_event(db, "magic_link_consume_failed", reason="invalid_or_expired")
        await db.commit()
        return None

    result = await db.execute(select(User).where(User.id == record.user_id))
    user = result.scalar_one_or_none()
    if not user:
        await db.commit()
        return None

    record.used = True
    token_pair = _issue_token_pair(user, device_id="magic-link")

    new_refresh = RefreshToken(
        jti=token_pair["refresh_jti"],
        user_id=user.id,
        revoked=False,
        session_id=token_pair["session_id"],
        device_id="magic-link",
        created_at=int(time.time()),
        expires_at=int(time.time()) + REFRESH_TOKEN_EXPIRE_SECONDS,
    )
    db.add(new_refresh)
    await _log_event(
        db,
        "magic_link_consume_success",
        user_id=user.id,
        session_id=token_pair["session_id"],
    )
    await db.commit()
    return {k: v for k, v in token_pair.items() if k != "refresh_jti"}
