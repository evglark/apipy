from apipy.auth.security import decode_jwt, hash_password
from apipy.auth.service import login_user, logout_user, refresh_access_token, register_user


def test_login_user_success_returns_token_pair_with_session_claims():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = [{"user_id": 1, "password_hash": hash_password("password123")}]
    refresh_tokens_db = []
    login_attempts_db = {}
    events = []

    result = login_user(
        "Alice", "password123", users_db, credentials_db, refresh_tokens_db, login_attempts_db, events, "iphone"
    )

    assert result is not None
    assert "access_token" in result
    claims = decode_jwt(result["access_token"])
    assert claims["iss"]
    assert claims["aud"]
    assert claims["device_id"] == "iphone"


def test_refresh_rotation_revokes_previous_refresh():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = []
    refresh_tokens_db = []
    login_attempts_db = {}
    events = []

    register_user("Bob", "bob-secret", users_db, credentials_db, events)
    tokens = login_user("Bob", "bob-secret", users_db, credentials_db, refresh_tokens_db, login_attempts_db, events)

    refreshed = refresh_access_token(tokens["refresh_token"], refresh_tokens_db, events)
    assert refreshed is not None
    assert refreshed["refresh_token"] != tokens["refresh_token"]
    assert refresh_access_token(tokens["refresh_token"], refresh_tokens_db, events) is None


def test_refresh_and_logout_flow():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = []
    refresh_tokens_db = []
    login_attempts_db = {}
    blacklist = set()
    events = []

    register_user("Alice2", "secret", users_db, credentials_db, events)
    tokens = login_user("Alice2", "secret", users_db, credentials_db, refresh_tokens_db, login_attempts_db, events)

    assert logout_user(tokens["refresh_token"], refresh_tokens_db, blacklist, events)
    assert tokens["refresh_token"] in blacklist
    assert any(e["event"] == "logout_success" for e in events)
