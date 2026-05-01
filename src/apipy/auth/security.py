import time
import uuid
from os import getenv

from passlib.context import CryptContext

SECRET_KEY = getenv("API_SECRET_KEY")
JWT_ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
JWT_PRIVATE_KEY = getenv("JWT_PRIVATE_KEY")
JWT_PUBLIC_KEY = getenv("JWT_PUBLIC_KEY")
JWT_ISSUER = getenv("JWT_ISSUER", "apipy")
JWT_AUDIENCE = getenv("JWT_AUDIENCE", "apipy-clients")
ACCESS_TOKEN_EXPIRE_SECONDS = int(getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "900"))
REFRESH_TOKEN_EXPIRE_SECONDS = int(getenv("REFRESH_TOKEN_EXPIRE_SECONDS", "604800"))
MAX_LOGIN_ATTEMPTS = int(getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOGIN_BLOCK_SECONDS = int(getenv("LOGIN_BLOCK_SECONDS", "60"))
IP_RATE_LIMIT_ATTEMPTS = int(getenv("IP_RATE_LIMIT_ATTEMPTS", "20"))
IP_RATE_LIMIT_WINDOW_SECONDS = int(getenv("IP_RATE_LIMIT_WINDOW_SECONDS", "60"))

_pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return _pwd_context.verify(password, stored_hash)


def create_jwt(payload: dict, expires_in_seconds: int) -> str:
    import jwt

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
    import jwt

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
