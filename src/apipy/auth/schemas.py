from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    password: str


class LoginRequest(BaseModel):
    name: str
    password: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RegisterResponse(BaseModel):
    id: int
    name: str


class UserClaims(BaseModel):
    sub: str
    user_id: int
    scope: str
    type: str
    iat: int
    exp: int
