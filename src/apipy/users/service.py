from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apipy.users.models import User


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()


async def get_user_by_id(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(data: dict, db: AsyncSession):
    new_user = User(
        name=data["name"],
        email=data["email"],
        role=data.get("role", "user"),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(user_id: int, data: dict, db: AsyncSession):
    user = await get_user_by_id(user_id, db)
    if not user:
        return None

    user.name = data["name"]
    user.email = data["email"]
    user.role = data.get("role", user.role)
    await db.commit()
    await db.refresh(user)
    return user


async def patch_user(user_id: int, data: dict, db: AsyncSession):
    user = await get_user_by_id(user_id, db)
    if not user:
        return None

    for field, value in data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(user_id: int, db: AsyncSession):
    user = await get_user_by_id(user_id, db)
    if not user:
        return None

    await db.delete(user)
    await db.commit()
    return user
