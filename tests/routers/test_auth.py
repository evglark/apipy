from fastapi.testclient import TestClient

from apipy.main import app

client = TestClient(app)


def test_register():
    response = client.post(
        "/auth/register",
        json={"username": "student", "password": "password123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "registered"
    assert payload["user"]["username"] == "student"


def test_register_duplicate_username_returns_409():
    client.post(
        "/auth/register",
        json={"username": "student", "password": "password123"},
    )

    response = client.post(
        "/auth/register",
        json={"username": "student", "password": "password123"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}


def test_login_success():
    client.post(
        "/auth/register",
        json={"username": "student", "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"username": "student", "password": "password123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["user_id"] == 1
    assert payload["access_token"]


def test_login_invalid_credentials_returns_401():
    response = client.post(
        "/auth/login",
        json={"username": "student", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}
