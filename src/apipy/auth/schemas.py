from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    password: str


class LoginRequest(BaseModel):
    name: str
    password: str
    device_id: str | None = None


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    session_id: str


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
    session_id: str
    device_id: str
    iat: int
    exp: int
    iss: str
    aud: str
