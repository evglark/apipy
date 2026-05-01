import time
from sqlalchemy.ext.asyncio import AsyncSession

from apipy.auth.models import SecurityEvent


async def _log_event(
    db: AsyncSession, event: str, user_id: int | None = None, **details
):
    new_event = SecurityEvent(
        event=event, ts=int(time.time()), user_id=user_id, details=str(details)
    )
    db.add(new_event)
