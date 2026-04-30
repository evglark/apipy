from fastapi import APIRouter, HTTPException

from apipy.auth.schemas import LoginRequest, LoginResponse
from apipy.auth.service import login_user
from apipy.users.models import fake_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    login_result = login_user(payload.name, payload.password, fake_db)
    if not login_result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return login_result
