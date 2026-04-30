import time
import uuid
from os import getenv

from passlib.context import CryptContext

SECRET_KEY = getenv("API_SECRET_KEY", "dev-secret-change-me")
JWT_ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
JWT_PRIVATE_KEY = getenv(
    "JWT_PRIVATE_KEY",
    "-----BEGIN PRIVATE KEY-----\n"
    "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDncX7V+o56lrGx\n"
    "P8P2KL9J3WFuY4FeYfESfKHmA2f8Siutd4N7Mm50JX5fBfjOCSI3WN4hjmDfrjOj\n"
    "9JqgFPxao6f0f42xwGA0iUVfSaPy1lN+4YKE3PpvCxB9zl6udEOG+yL+At7m39Lm\n"
    "WSw96qnRvGN8xbgQdPvjHzknf9RShEu6d2RsQb/6fuWp8Nr0q5L4YJf9E4jR7Hu5\n"
    "l8sVVp8CU6fHUVvQWWc8Y2QST4lS1TAAIZY//dbSHIY7AHQqW0qKs4xF2S6Bth7q\n"
    "vAaQQ/Tpm4Sckf6M6nCy3CC+mvf5k9j8poe/g3X6wSJQ2P8wQa7A9mLQOD2KvHdn\n"
    "DzOHBUsTAgMBAAECggEAP4R6k5GxlEsM8PzPm4j32+fgT9NxkNfscu6s5r8QxjL+\n"
    "dSCt0q0LZWqk60QN4qf8DfA6fM4Jz6KXVoC5/sq6oDkZ6V7V1A6/qkJC4gwY+IhY\n"
    "WxwAPSL9JkLBok3vci3Eaf1JKco3juTYO4u8gpAFmCZspMdGxlzb/p7fYjvXgrm4\n"
    "5GN+cdoAS3WQjKCicw6jD9jQfxg8Ehg+Oi7vF6vdMFW6n2aL4Vu6+f8TAjSfNT0Q\n"
    "G57Rz81ecgE4OQzGyY/Q81AOKwDd4IO/2YxPIzIyEABji0xK6Q5Jr9a4V0ACwcx4\n"
    "1xrW8bNTHubRxGQ4e4IT8vWf0AL4wmYbtU0hO8mX8QKBgQD8Ks7MFh2YQH8F3xFZ\n"
    "xQv1fIY2xYjl2H5xbROw4bQxB8xSImk5gc7VDkC2M3h0D4Pjfq3RuYQvTAwQmQ3u\n"
    "2YI1Vfd1kJTT48A8M5kdnyw+q7Ky4hSx6CkA9/wLz9M6v4x5eCfv7W7Sa9AoLx+e\n"
    "8Ec2kPqv0QDYwqEvWWi/21hylQKBgQDrWXVv3I4jR3aWaqQJ5xDa4F/FRz23dN9v\n"
    "M8e8xh9qfeVh9+soD0h09f2gAF0x+Q6fN7Lf+alFUK9rWb3Yk86FR5W+nlXY7jBf\n"
    "i7AX5nqvPgTJ5LM2I9fQ8vXRqQJ2vP5IYVm2KW5ziGvDG1R6W6S9u7uW+AJ+B5yt\n"
    "5fHhOHWzYwKBgQCOowIvL3qK8RMo7Yf4QvGJYzKdr1dCINzP2/UdYBkPEgsYMrDY\n"
    "kewSRkX7hXxV1iQkE1g3zD0D1b+o6FQm3sV8I4bvgk1uZeJ1D8sE7jXFD4ad5z4a\n"
    "f+2MMk5zsM7V6zbX+vMuaNY8qYMYW6UWp5TtHnX7kqYt0TjZ4AZ8Q6QowQKBgQDJ\n"
    "iJ+fYFn8vRVu8d+S3Ohq6d4i4lvbxTKVfU58vI2g0k7BChMxR5lzc8W9vMYa7W9k\n"
    "a+5Qm6w7Cj19nMwlBm4fH9w37w3I9Z5iYOHuW2QW4L4T0l2hwl3BXfNNy2A3G31j\n"
    "qMUtq6pRrM0M2f3rV6T8owm9dLqIGJxXf8FL84BVEQKBgQDA6C9xW7nlxT9KdHVV\n"
    "5HFZCL9q9v0R3pYg6gK7i8V8kgnr4wH4P3P3GmMk9Q3/R8n5e1JxXk/94EybmEw0\n"
    "P6t6xkV5wD5fG8H6zqu+rOIJ6wYx7eS1mtRl7r8J7L0X9N2OYFz+Kqzqk3otw0lO\n"
    "L+S3vP5A0zB4U90SHk0KJQ==\n"
    "-----END PRIVATE KEY-----",
)
JWT_PUBLIC_KEY = getenv(
    "JWT_PUBLIC_KEY",
    "-----BEGIN PUBLIC KEY-----\n"
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA53F+1fqOepaxsT/D9ii/\n"
    "Sd1hbmOBXmHxEnyh5gNn/EorrXeDezJudCV+XwX4zgkiN1jeIY5g364zo/SaoBT8\n"
    "WqOn9H+NscBgNIlFX0mj8tZTfuGChNz6bwsQfc5ernRDhvsi/gLe5t/S5lksPeqp\n"
    "0bxjfMW4EHT74x85J3/UUoRLundkbEG/+n7lqfDa9KuS+GCX/ROI0ex7uZfLFVaf\n"
    "AlOnx1Fb0FlnPGNkEk+JUtUwACGWP/3W0hyGOwB0KltKirOMRdkugbYe6rwGkEP0\n"
    "6ZuEnJH+jOpwstwgvpr3+ZPY/KaHv4N1+sEiUNj/MEGuwPZi0Dg9irx3Zw8zhwVL\n"
    "EwIDAQAB\n"
    "-----END PUBLIC KEY-----",
)
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
