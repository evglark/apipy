import base64
import hashlib
import hmac
import json
import secrets
import time
from os import getenv

SECRET_KEY = getenv("API_SECRET_KEY", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_SECONDS = int(getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "900"))
REFRESH_TOKEN_EXPIRE_SECONDS = int(getenv("REFRESH_TOKEN_EXPIRE_SECONDS", "604800"))
MAX_LOGIN_ATTEMPTS = int(getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOGIN_BLOCK_SECONDS = int(getenv("LOGIN_BLOCK_SECONDS", "60"))


def hash_password(password: str, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt_value.encode(), 100_000)
    return f"{salt_value}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt, _ = stored_hash.split("$", maxsplit=1)
    expected = hash_password(password, salt)
    return hmac.compare_digest(expected, stored_hash)


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_jwt(payload: dict, expires_in_seconds: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    body = payload.copy()
    body["iat"] = int(time.time())
    body["exp"] = int(time.time()) + expires_in_seconds

    header_encoded = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    body_encoded = _b64url_encode(json.dumps(body, separators=(",", ":")).encode())
    message = f"{header_encoded}.{body_encoded}".encode()
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
    signature_encoded = _b64url_encode(signature)
    return f"{header_encoded}.{body_encoded}.{signature_encoded}"


def decode_jwt(token: str) -> dict | None:
    try:
        header_encoded, body_encoded, signature_encoded = token.split(".")
        message = f"{header_encoded}.{body_encoded}".encode()
        expected_signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
        received_signature = _b64url_decode(signature_encoded)
        if not hmac.compare_digest(expected_signature, received_signature):
            return None

        payload = json.loads(_b64url_decode(body_encoded))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
