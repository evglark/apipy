import asyncio
import time

from sqlalchemy import delete

from apipy.auth.models import IPRateLimitAttempt, LoginAttempt, RefreshToken
from apipy.database import async_session
from apipy.auth.constants import (
    CLEANUP_INTERVAL_SECONDS,
    REVOKED_REFRESH_TOKEN_RETENTION_SECONDS,
    IP_RATE_LIMIT_RETENTION_SECONDS,
)


async def run_cleanup_once() -> None:
    now = int(time.time())
    async with async_session() as db:
        await db.execute(
            delete(RefreshToken).where(
                RefreshToken.revoked.is_(True),
                RefreshToken.created_at < now - REVOKED_REFRESH_TOKEN_RETENTION_SECONDS,
            )
        )
        await db.execute(
            delete(IPRateLimitAttempt).where(
                IPRateLimitAttempt.ts < now - IP_RATE_LIMIT_RETENTION_SECONDS
            )
        )
        await db.execute(delete(LoginAttempt).where(LoginAttempt.blocked_until < now))
        await db.commit()


async def cleanup_loop() -> None:
    while True:
        await run_cleanup_once()
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
