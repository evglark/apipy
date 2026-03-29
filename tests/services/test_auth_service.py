from apipy.services.auth_service import (
    get_auth_user_by_username,
    login_user,
    register_user,
)


def test_register_user_creates_record():
    users_db = []

    created_user = register_user("student", "password123", users_db)

    assert created_user == {"id": 1, "username": "student"}
    assert len(users_db) == 1
    assert users_db[0]["password_hash"] != "password123"
    assert users_db[0]["salt"]


def test_get_auth_user_by_username_returns_none_for_missing_user():
    users_db = [{"id": 1, "username": "student", "password_hash": "x", "salt": "y"}]

    result = get_auth_user_by_username("unknown", users_db)

    assert result is None


def test_login_user_returns_token_for_valid_credentials():
    users_db = []
    sessions_db = {}
    register_user("student", "password123", users_db)

    login_result = login_user("student", "password123", users_db, sessions_db)

    assert login_result is not None
    assert login_result["user_id"] == 1
    assert login_result["access_token"] in sessions_db


def test_login_user_returns_none_for_invalid_password():
    users_db = []
    sessions_db = {}
    register_user("student", "password123", users_db)

    login_result = login_user("student", "wrong", users_db, sessions_db)

    assert login_result is None
    assert sessions_db == {}
