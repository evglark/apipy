import time
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apipy.auth.models import MagicToken, RefreshToken
from apipy.auth.constants import REFRESH_TOKEN_EXPIRE_SECONDS
from apipy.auth.utils.events import _log_event
from apipy.auth.utils.queries import _find_user_by_email, _get_role_permissions
from apipy.auth.utils.tokens import _issue_token_pair
from apipy.users.models import User


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
    permissions = await _get_role_permissions(user.role, db)
    token_pair = _issue_token_pair(
        user, device_id="magic-link", permissions=permissions
    )

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
