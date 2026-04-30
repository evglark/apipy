from fastapi.testclient import TestClient

from apipy.auth.models import security_events_db
from apipy.main import app

client = TestClient(app)


def test_register_success():
    response = client.post("/auth/register", json={"name": "Bob", "email": "bob@example.com", "password": "bob-secret"})

    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Bob", "email": "bob@example.com"}


def test_login_refresh_rotation_me_logout_success():
    client.post("/auth/register", json={"name": "Bob", "email": "bob@example.com", "password": "bob-secret"})
    login_response = client.post("/auth/login", json={"name": "Bob", "password": "bob-secret", "device_id": "web"})

    assert login_response.status_code == 200
    tokens = login_response.json()

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me_response.status_code == 200
    assert me_response.json()["name"] == "Bob"
    assert me_response.json()["device_id"] == "web"

    refresh_response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_response.status_code == 200
    rotated = refresh_response.json()
    assert rotated["refresh_token"] != tokens["refresh_token"]

    old_refresh_reuse = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert old_refresh_reuse.status_code == 401

    logout_response = client.post("/auth/logout", json={"refresh_token": rotated["refresh_token"]})
    assert logout_response.status_code == 200


def test_bruteforce_protection_and_security_logging():
    for _ in range(5):
        response = client.post("/auth/login", json={"name": "Alice", "password": "wrong"})
        assert response.status_code == 401

    blocked_response = client.post("/auth/login", json={"name": "Alice", "password": "wrong"})
    assert blocked_response.status_code == 429
    assert any(event["event"] in {"login_failed", "login_blocked"} for event in security_events_db)


def test_magic_link_flow_and_remote_session_logout():
    login_response = client.post("/auth/login", json={"name": "Alice", "password": "password123", "device_id": "ios"})
    assert login_response.status_code == 200
    first_session = login_response.json()["session_id"]

    magic_create = client.post("/auth/magic-link/request", json={"email": "alice@example.com"})
    assert magic_create.status_code == 200
    token = magic_create.json()["token"]

    magic_consume = client.post("/auth/magic-link/consume", json={"token": token})
    assert magic_consume.status_code == 200
    magic_tokens = magic_consume.json()

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": magic_tokens["refresh_token"], "session_id": first_session},
    )
    assert logout_response.status_code == 200
