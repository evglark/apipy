from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    password: str


class LoginRequest(BaseModel):
    name: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    id: int
    name: str
