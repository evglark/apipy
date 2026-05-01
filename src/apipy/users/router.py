from fastapi import APIRouter, HTTPException

from apipy.users.schemas import User, UserCreate, UserUpdate
from apipy.users.service import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    get_all_users,
    get_user_by_id,
    patch_user as patch_user_service,
    update_user as update_user_service,
)

from apipy.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from apipy.auth.deps import require_roles

router = APIRouter(prefix="/users")


@router.get("/", response_model=list[User])
async def get_users(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "user", "read_only")),
):
    return await get_all_users(db)


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "user", "read_only")),
):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    return await create_user_service(user.model_dump(), db)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "user")),
):
    updated_user = await update_user_service(user_id, user.model_dump(), db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.patch("/{user_id}", response_model=User)
async def patch_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin", "user")),
):
    updated_user = await patch_user_service(
        user_id, user.model_dump(exclude_unset=True), db
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    user = await delete_user_service(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": f"user {user_id} deleted"}
