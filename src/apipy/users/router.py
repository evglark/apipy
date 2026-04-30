from fastapi import APIRouter, HTTPException

from apipy.storage import STATE
from apipy.users.schemas import User, UserCreate, UserUpdate
from apipy.users.service import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    get_all_users,
    get_user_by_id,
    patch_user as patch_user_service,
    update_user as update_user_service,
)

router = APIRouter(prefix="/users")


@router.get("/", response_model=list[User])
def get_users():
    return get_all_users(STATE["users"])


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    user = get_user_by_id(user_id, STATE["users"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User)
def create_user(user: UserCreate):
    return create_user_service(user.model_dump(), STATE["users"])


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserCreate):
    updated_user = update_user_service(user_id, user.model_dump(), STATE["users"])
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.patch("/{user_id}", response_model=User)
def patch_user(user_id: int, user: UserUpdate):
    updated_user = patch_user_service(user_id, user.model_dump(exclude_unset=True), STATE["users"])
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}")
def delete_user(user_id: int):
    user = delete_user_service(user_id, STATE["users"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": f"user {user_id} deleted"}
