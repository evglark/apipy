import time
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apipy.auth.models import Credential, EmailVerificationToken
from apipy.auth.security import hash_password
from apipy.auth.utils.events import _log_event
from apipy.auth.utils.queries import _find_user_by_email, _find_user_by_name
from apipy.users.models import User

EMAIL_VERIFICATION_TTL_SECONDS = 24 * 60 * 60


async def register_user(
    name: str, email: str, password: str, db: AsyncSession, role: str = "user"
):
    user = await _find_user_by_name(name, db) or await _find_user_by_email(email, db)
    if user:
        await _log_event(db, "register_failed", username=name, reason="exists")
        await db.commit()
        return None

    new_user = User(name=name, email=email, role=role)
    db.add(new_user)
    await db.flush()

    new_cred = Credential(user_id=new_user.id, password_hash=hash_password(password))
    db.add(new_cred)
    db.add(
        EmailVerificationToken(
            token=str(uuid.uuid4()),
            user_id=new_user.id,
            exp=int(time.time()) + EMAIL_VERIFICATION_TTL_SECONDS,
            used=False,
        )
    )

    await _log_event(db, "register_success", user_id=new_user.id)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def verify_email_token(token: str, db: AsyncSession):
    now = int(time.time())
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    )
    record = result.scalar_one_or_none()
    if not record or record.used or record.exp < now:
        await _log_event(db, "email_verification_failed", reason="invalid_or_expired")
        await db.commit()
        return False

    result = await db.execute(select(User).where(User.id == record.user_id))
    user = result.scalar_one_or_none()
    if not user:
        await db.commit()
        return False

    user.email_verified = True
    record.used = True
    await _log_event(db, "email_verified", user_id=user.id)
    await db.commit()
    return True


async def resend_verification_email(email: str, db: AsyncSession):
    user = await _find_user_by_email(email, db)
    if user and not user.email_verified:
        db.add(
            EmailVerificationToken(
                token=str(uuid.uuid4()),
                user_id=user.id,
                exp=int(time.time()) + EMAIL_VERIFICATION_TTL_SECONDS,
                used=False,
            )
        )
        await _log_event(db, "email_verification_resent", user_id=user.id)
    else:
        await _log_event(db, "email_verification_resent", email=email, user_exists=False)
    await db.commit()
    return {"status": "ok"}
