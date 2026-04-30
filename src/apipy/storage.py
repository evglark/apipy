"""In-memory storage and seed helpers.

Single source of truth for runtime state used by routers/services.
"""

from apipy.auth.security import hash_password


def build_seed_state() -> dict:
    users = [{"id": 1, "name": "Alice", "email": "alice@example.com"}]
    credentials = [{"user_id": 1, "password_hash": hash_password("password123")}]
    return {
        "users": users,
        "credentials": credentials,
        "refresh_tokens": [],
        "token_blacklist": set(),
        "login_attempts": {},
        "ip_rate_limit": {},
        "security_events": [],
        "magic_tokens": [],
    }


STATE = build_seed_state()


def reset_state_with_seeds() -> None:
    global STATE
    STATE = build_seed_state()
