from apipy.auth.security import hash_password
from apipy.auth.service import login_user, logout_user, refresh_access_token, register_user


def test_login_user_success_returns_token_pair():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = [{"user_id": 1, "password_hash": hash_password("password123")}]
    refresh_tokens_db = []
    login_attempts_db = {}

    result = login_user("Alice", "password123", users_db, credentials_db, refresh_tokens_db, login_attempts_db)

    assert result is not None
    assert "access_token" in result
    assert "refresh_token" in result


def test_register_and_login_flow():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = []
    refresh_tokens_db = []
    login_attempts_db = {}

    user = register_user("Bob", "bob-secret", users_db, credentials_db)
    result = login_user("Bob", "bob-secret", users_db, credentials_db, refresh_tokens_db, login_attempts_db)

    assert user == {"id": 2, "name": "Bob"}
    assert result is not None


def test_refresh_and_logout_flow():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = []
    refresh_tokens_db = []
    login_attempts_db = {}
    blacklist = set()

    register_user("Alice2", "secret", users_db, credentials_db)
    tokens = login_user("Alice2", "secret", users_db, credentials_db, refresh_tokens_db, login_attempts_db)

    refreshed = refresh_access_token(tokens["refresh_token"], refresh_tokens_db)
    assert refreshed is not None

    assert logout_user(tokens["refresh_token"], refresh_tokens_db, blacklist)
    assert tokens["refresh_token"] in blacklist
