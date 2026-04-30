from apipy.auth.service import login_user, register_user


def test_register_user_creates_record():
    users_db = []
    credentials_db = []
    security_events_db = []

    created_user = register_user("student", "student@example.com", "password123", users_db, credentials_db, security_events_db)

    assert created_user == {"id": 1, "name": "student", "email": "student@example.com"}
    assert len(users_db) == 1
    assert credentials_db[0]["password_hash"] != "password123"


def test_login_user_returns_none_for_invalid_password():
    users_db = []
    credentials_db = []
    refresh_tokens_db = []
    login_attempts_db = {}
    security_events_db = []

    register_user("student", "student@example.com", "password123", users_db, credentials_db, security_events_db)

    login_result = login_user(
        "student",
        "wrong",
        users_db,
        credentials_db,
        refresh_tokens_db,
        login_attempts_db,
        security_events_db,
    )

    assert login_result is None


def test_login_user_returns_tokens_for_valid_credentials():
    users_db = []
    credentials_db = []
    refresh_tokens_db = []
    login_attempts_db = {}
    security_events_db = []

    register_user("student", "student@example.com", "password123", users_db, credentials_db, security_events_db)

    login_result = login_user(
        "student",
        "password123",
        users_db,
        credentials_db,
        refresh_tokens_db,
        login_attempts_db,
        security_events_db,
        device_id="test-device",
    )

    assert login_result is not None
    assert login_result["token_type"] == "bearer"
    assert login_result["access_token"]
    assert login_result["refresh_token"]
    assert login_result["session_id"]
    assert len(refresh_tokens_db) == 1
