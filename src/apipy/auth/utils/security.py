import time
import uuid
import hashlib
from passlib.context import CryptContext
import jwt

from apipy.auth.constants import (
    SECRET_KEY,
    JWT_ALGORITHM,
    JWT_PRIVATE_KEY,
    JWT_PUBLIC_KEY,
    JWT_ISSUER,
    JWT_AUDIENCE,
)

_pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return _pwd_context.verify(password, stored_hash)


def create_jwt(payload: dict, expires_in_seconds: int) -> str:
    now = int(time.time())
    body = payload.copy()
    body.update(
        {
            "iat": now,
            "exp": now + expires_in_seconds,
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
        }
    )
    if JWT_ALGORITHM.startswith("HS"):
        return jwt.encode(body, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return jwt.encode(body, JWT_PRIVATE_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict | None:
    try:
        key = SECRET_KEY if JWT_ALGORITHM.startswith("HS") else JWT_PUBLIC_KEY
        return jwt.decode(
            token,
            key,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
    except Exception:
        return None


def new_session_id() -> str:
    return str(uuid.uuid4())


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
