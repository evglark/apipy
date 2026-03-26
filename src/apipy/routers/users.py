from fastapi import APIRouter, HTTPException
from apipy.models.user import User, UserCreate, UserUpdate
from apipy.services.user_service import (
    get_all_users,
    get_user_by_id,
    create_user as create_user_service,
    update_user as update_user_service,
    patch_user as patch_user_service,
    delete_user as delete_user_service,
)

router = APIRouter(prefix="/users")

# --- "база" (пока просто в памяти) ---
fake_db = [{"id": 1, "name": "Alice"}]


@router.get("/", response_model=list[User])
def get_users():
    return get_all_users(fake_db)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    user = get_user_by_id(user_id, fake_db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User)
def create_user(user: UserCreate):
    return create_user_service(user.model_dump(), fake_db)


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserCreate):
    updated_user = update_user_service(user_id, user.model_dump(), fake_db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.patch("/{user_id}", response_model=User)
def patch_user(user_id: int, user: UserUpdate):
    updated_user = patch_user_service(
        user_id, user.model_dump(exclude_unset=True), fake_db
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}")
def delete_user(user_id: int):
    user = delete_user_service(user_id, fake_db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": f"user {user_id} deleted"}
