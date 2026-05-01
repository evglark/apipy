from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apipy.users.models import Role, User


async def _find_user_by_name(name: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.name == name))
    return result.scalar_one_or_none()


async def _find_user_by_email(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def _get_role_permissions(role: str, db: AsyncSession) -> list[str]:
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.name == role)
    )
    role_model = result.scalar_one_or_none()
    if not role_model:
        return []
    return [permission.name for permission in role_model.permissions]
