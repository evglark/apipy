import time
import uuid

from apipy.auth.security import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    LOGIN_BLOCK_SECONDS,
    MAX_LOGIN_ATTEMPTS,
    REFRESH_TOKEN_EXPIRE_SECONDS,
    create_jwt,
    decode_jwt,
    hash_password,
    verify_password,
)
from apipy.users.service import create_user, get_all_users


def _find_user_by_name(name: str, users_db):
    for user in get_all_users(users_db):
        if user["name"] == name:
            return user
    return None


def _is_blocked(name: str, login_attempts_db):
    record = login_attempts_db.get(name)
    if not record:
        return False
    return record.get("blocked_until", 0) > int(time.time())


def _register_failed_attempt(name: str, login_attempts_db):
    now = int(time.time())
    record = login_attempts_db.setdefault(name, {"count": 0, "blocked_until": 0})
    record["count"] += 1
    if record["count"] >= MAX_LOGIN_ATTEMPTS:
        record["blocked_until"] = now + LOGIN_BLOCK_SECONDS


def _reset_failed_attempts(name: str, login_attempts_db):
    login_attempts_db.pop(name, None)


def login_user(name: str, password: str, users_db, credentials_db, refresh_tokens_db, login_attempts_db):
    if _is_blocked(name, login_attempts_db):
        return {"error": "Too many login attempts. Try again later."}

    user = _find_user_by_name(name, users_db)
    if not user:
        _register_failed_attempt(name, login_attempts_db)
        return None

    for credentials in credentials_db:
        if credentials["user_id"] == user["id"] and verify_password(password, credentials["password_hash"]):
            _reset_failed_attempts(name, login_attempts_db)
            access_claims = {"sub": name, "user_id": user["id"], "scope": "access", "type": "access"}
            refresh_jti = str(uuid.uuid4())
            refresh_claims = {
                "sub": name,
                "user_id": user["id"],
                "scope": "refresh",
                "type": "refresh",
                "jti": refresh_jti,
            }
            access_token = create_jwt(access_claims, ACCESS_TOKEN_EXPIRE_SECONDS)
            refresh_token = create_jwt(refresh_claims, REFRESH_TOKEN_EXPIRE_SECONDS)
            refresh_tokens_db.append({"jti": refresh_jti, "user_id": user["id"], "revoked": False})
            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    _register_failed_attempt(name, login_attempts_db)
    return None


def refresh_access_token(refresh_token: str, refresh_tokens_db):
    payload = decode_jwt(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None

    jti = payload.get("jti")
    token_record = next((item for item in refresh_tokens_db if item["jti"] == jti), None)
    if not token_record or token_record["revoked"]:
        return None

    access_claims = {
        "sub": payload["sub"],
        "user_id": payload["user_id"],
        "scope": "access",
        "type": "access",
    }
    return {"access_token": create_jwt(access_claims, ACCESS_TOKEN_EXPIRE_SECONDS), "token_type": "bearer"}


def logout_user(refresh_token: str, refresh_tokens_db, token_blacklist):
    payload = decode_jwt(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return False

    token_blacklist.add(refresh_token)
    for item in refresh_tokens_db:
        if item["jti"] == payload.get("jti"):
            item["revoked"] = True
            return True
    return False


def register_user(name: str, password: str, users_db, credentials_db):
    user = _find_user_by_name(name, users_db)
    if user:
        return None

    created_user = create_user({"name": name}, users_db)
    credentials_db.append({"user_id": created_user["id"], "password_hash": hash_password(password)})
    return created_user
