from fastapi import APIRouter, HTTPException

from apipy.auth.models import fake_credentials_db
from apipy.auth.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from apipy.auth.service import login_user, register_user
from apipy.users.models import fake_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    created_user = register_user(payload.name, payload.password, fake_db, fake_credentials_db)
    if not created_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return created_user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    login_result = login_user(payload.name, payload.password, fake_db, fake_credentials_db)
    if not login_result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return login_result
