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
    new_session_id,
    verify_password,
)
from apipy.users.service import create_user, get_all_users


def _log_event(security_events_db, event: str, **details):
    security_events_db.append({"event": event, "ts": int(time.time()), **details})


def _find_user_by_name(name: str, users_db):
    for user in get_all_users(users_db):
        if user["name"] == name:
            return user
    return None


def _find_user_by_email(email: str, users_db):
    for user in get_all_users(users_db):
        if user.get("email") == email:
            return user
    return None


def _issue_token_pair(user: dict, device_id: str | None = None, session_id: str | None = None):
    session_id = session_id or new_session_id()
    effective_device_id = device_id or "unknown"
    access_claims = {
        "sub": user["name"],
        "user_id": user["id"],
        "scope": "access",
        "type": "access",
        "session_id": session_id,
        "device_id": effective_device_id,
    }
    refresh_jti = str(uuid.uuid4())
    refresh_claims = {
        "sub": user["name"],
        "user_id": user["id"],
        "scope": "refresh",
        "type": "refresh",
        "jti": refresh_jti,
        "session_id": session_id,
        "device_id": effective_device_id,
    }
    return {
        "access_token": create_jwt(access_claims, ACCESS_TOKEN_EXPIRE_SECONDS),
        "refresh_token": create_jwt(refresh_claims, REFRESH_TOKEN_EXPIRE_SECONDS),
        "token_type": "bearer",
        "session_id": session_id,
        "refresh_jti": refresh_jti,
    }


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


def login_user(
    name: str,
    password: str,
    users_db,
    credentials_db,
    refresh_tokens_db,
    login_attempts_db,
    security_events_db,
    device_id: str | None = None,
):
    if _is_blocked(name, login_attempts_db):
        _log_event(security_events_db, "login_blocked", username=name)
        return {"error": "Too many login attempts. Try again later."}

    user = _find_user_by_name(name, users_db)
    if not user:
        _register_failed_attempt(name, login_attempts_db)
        _log_event(security_events_db, "login_failed", username=name, reason="user_not_found")
        return None

    for credentials in credentials_db:
        if credentials["user_id"] == user["id"] and verify_password(password, credentials["password_hash"]):
            _reset_failed_attempts(name, login_attempts_db)
            token_pair = _issue_token_pair(user, device_id)
            refresh_tokens_db.append(
                {
                    "jti": token_pair["refresh_jti"],
                    "user_id": user["id"],
                    "revoked": False,
                    "session_id": token_pair["session_id"],
                    "device_id": device_id or "unknown",
                }
            )
            _log_event(security_events_db, "login_success", user_id=user["id"], session_id=token_pair["session_id"])
            return {k: v for k, v in token_pair.items() if k != "refresh_jti"}

    _register_failed_attempt(name, login_attempts_db)
    _log_event(security_events_db, "login_failed", username=name, reason="bad_password")
    return None


def refresh_access_token(refresh_token: str, refresh_tokens_db, security_events_db):
    payload = decode_jwt(refresh_token)
    if not payload or payload.get("type") != "refresh":
        _log_event(security_events_db, "refresh_failed", reason="invalid_token")
        return None

    jti = payload.get("jti")
    token_record = next((item for item in refresh_tokens_db if item["jti"] == jti), None)
    if not token_record or token_record["revoked"]:
        _log_event(security_events_db, "refresh_failed", reason="revoked_or_missing", jti=jti)
        return None

    token_record["revoked"] = True
    new_jti = str(uuid.uuid4())
    refresh_tokens_db.append(
        {
            "jti": new_jti,
            "user_id": payload["user_id"],
            "revoked": False,
            "session_id": payload.get("session_id"),
            "device_id": payload.get("device_id"),
        }
    )

    access_claims = {
        "sub": payload["sub"],
        "user_id": payload["user_id"],
        "scope": "access",
        "type": "access",
        "session_id": payload.get("session_id", ""),
        "device_id": payload.get("device_id", "unknown"),
    }
    new_refresh_claims = {
        "sub": payload["sub"],
        "user_id": payload["user_id"],
        "scope": "refresh",
        "type": "refresh",
        "jti": new_jti,
        "session_id": payload.get("session_id", ""),
        "device_id": payload.get("device_id", "unknown"),
    }
    _log_event(security_events_db, "refresh_rotated", user_id=payload["user_id"], old_jti=jti, new_jti=new_jti)
    return {
        "access_token": create_jwt(access_claims, ACCESS_TOKEN_EXPIRE_SECONDS),
        "refresh_token": create_jwt(new_refresh_claims, REFRESH_TOKEN_EXPIRE_SECONDS),
        "token_type": "bearer",
        "session_id": payload.get("session_id", ""),
    }


def logout_user(refresh_token: str, refresh_tokens_db, token_blacklist, security_events_db, session_id: str | None = None):
    payload = decode_jwt(refresh_token)
    if not payload or payload.get("type") != "refresh":
        _log_event(security_events_db, "logout_failed", reason="invalid_token")
        return False

    token_blacklist.add(refresh_token)

    if session_id:
        revoked = False
        for item in refresh_tokens_db:
            if item.get("session_id") == session_id:
                item["revoked"] = True
                revoked = True
        if revoked:
            _log_event(security_events_db, "logout_session_success", user_id=payload.get("user_id"), session_id=session_id)
            return True

    for item in refresh_tokens_db:
        if item["jti"] == payload.get("jti"):
            item["revoked"] = True
            _log_event(security_events_db, "logout_success", user_id=payload.get("user_id"), jti=item["jti"])
            return True
    return False


def register_user(name: str, email: str, password: str, users_db, credentials_db, security_events_db):
    user = _find_user_by_name(name, users_db) or _find_user_by_email(email, users_db)
    if user:
        _log_event(security_events_db, "register_failed", username=name, reason="exists")
        return None

    created_user = create_user({"name": name, "email": email}, users_db)
    credentials_db.append({"user_id": created_user["id"], "password_hash": hash_password(password)})
    _log_event(security_events_db, "register_success", user_id=created_user["id"])
    return created_user


def create_magic_link(email: str, users_db, magic_tokens_db, security_events_db, ttl_seconds: int = 600):
    user = _find_user_by_email(email, users_db)
    if not user:
        _log_event(security_events_db, "magic_link_request_failed", email=email, reason="user_not_found")
        return None
    token = str(uuid.uuid4())
    magic_tokens_db.append({"token": token, "user_id": user["id"], "exp": int(time.time()) + ttl_seconds, "used": False})
    _log_event(security_events_db, "magic_link_created", user_id=user["id"])
    return {"token": token, "login_link": f"/auth/magic-link/consume?token={token}"}


def consume_magic_link(token: str, users_db, refresh_tokens_db, magic_tokens_db, security_events_db):
    now = int(time.time())
    record = next((item for item in magic_tokens_db if item["token"] == token), None)
    if not record or record["used"] or record["exp"] < now:
        _log_event(security_events_db, "magic_link_consume_failed", reason="invalid_or_expired")
        return None
    user = next((u for u in users_db if u["id"] == record["user_id"]), None)
    if not user:
        return None
    record["used"] = True
    token_pair = _issue_token_pair(user, device_id="magic-link")
    refresh_tokens_db.append(
        {"jti": token_pair["refresh_jti"], "user_id": user["id"], "revoked": False, "session_id": token_pair["session_id"], "device_id": "magic-link"}
    )
    _log_event(security_events_db, "magic_link_consume_success", user_id=user["id"], session_id=token_pair["session_id"])
    return {k: v for k, v in token_pair.items() if k != "refresh_jti"}
