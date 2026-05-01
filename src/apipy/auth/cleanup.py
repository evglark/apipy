import asyncio
import time

from sqlalchemy import delete

from apipy.auth.models import IPRateLimitAttempt, LoginAttempt, RefreshToken
from apipy.database import async_session

CLEANUP_INTERVAL_SECONDS = 3600
REVOKED_REFRESH_TOKEN_RETENTION_SECONDS = 7 * 24 * 3600
IP_RATE_LIMIT_RETENTION_SECONDS = 24 * 3600


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
