from fastapi.testclient import TestClient

from apipy.main import app

client = TestClient(app)


def test_register():
    response = client.post(
        "/auth/register",
        json={"name": "student", "email": "student@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "student"
    assert payload["email"] == "student@example.com"


def test_register_duplicate_returns_400():
    client.post(
        "/auth/register",
        json={"name": "student", "email": "student@example.com", "password": "password123"},
    )

    response = client.post(
        "/auth/register",
        json={"name": "student", "email": "student@example.com", "password": "password123"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}


def test_login_success():
    client.post(
        "/auth/register",
        json={"name": "student", "email": "student@example.com", "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"name": "student", "password": "password123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["session_id"]


def test_login_invalid_credentials_returns_401():
    response = client.post(
        "/auth/login",
        json={"name": "student", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
