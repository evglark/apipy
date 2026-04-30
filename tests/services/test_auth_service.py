from apipy.auth.service import login_user


def test_login_user_success():
    db = [{"id": 1, "name": "Alice"}]

    result = login_user("Alice", "password123", db)

    assert result == {"access_token": "token-1", "token_type": "bearer"}


def test_login_user_invalid_credentials():
    db = [{"id": 1, "name": "Alice"}]

    result = login_user("Alice", "wrong-password", db)

    assert result is None
