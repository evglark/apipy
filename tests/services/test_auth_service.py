from apipy.auth.service import login_user, register_user


def test_login_user_success():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = [{"user_id": 1, "password": "password123"}]

    result = login_user("Alice", "password123", users_db, credentials_db)

    assert result == {"access_token": "token-1", "token_type": "bearer"}


def test_login_user_invalid_credentials():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = [{"user_id": 1, "password": "password123"}]

    result = login_user("Alice", "wrong-password", users_db, credentials_db)

    assert result is None


def test_register_user_success():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = [{"user_id": 1, "password": "password123"}]

    result = register_user("Bob", "bob-secret", users_db, credentials_db)

    assert result == {"id": 2, "name": "Bob"}
    assert credentials_db[-1] == {"user_id": 2, "password": "bob-secret"}


def test_register_user_existing_name_returns_none():
    users_db = [{"id": 1, "name": "Alice"}]
    credentials_db = [{"user_id": 1, "password": "password123"}]

    result = register_user("Alice", "new-secret", users_db, credentials_db)

    assert result is None
    assert credentials_db == [{"user_id": 1, "password": "password123"}]
