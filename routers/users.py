from fastapi import APIRouter, HTTPException
from models.user import User, UserCreate

router = APIRouter(prefix="/users")

# --- "база" (пока просто в памяти) ---
fake_db = [{"id": 1, "name": "Alice"}]

@router.get("/", response_model=list[User])
def get_users():
    return fake_db


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in fake_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/", response_model=User)
def create_user(user: UserCreate):
    new_user = {"id": len(fake_db) + 1, "name": user.name}
    fake_db.append(new_user)
    return new_user


@router.delete("/{user_id}")
def delete_user(user_id: int):
    return {"status": f"user {user_id} deleted"}
