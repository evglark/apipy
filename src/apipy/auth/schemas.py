from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenPairResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    session_id: str


class RefreshRequest(BaseModel):
    session_id: str | None = None


class RegisterResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


class MagicLinkRequest(BaseModel):
    email: str


class MagicLinkConsumeRequest(BaseModel):
    token: str


class EmailVerificationResendRequest(BaseModel):
    email: str


class UserClaims(BaseModel):
    sub: str
    user_id: int
    scope: str
    role: str
    permissions: list[str] = []
    type: str
    session_id: str
    device_id: str
    iat: int
    exp: int
    iss: str
    aud: str
