from fastapi.testclient import TestClient

from apipy.main import app

client = TestClient(app)


def test_register_success():
    response = client.post("/auth/register", json={"name": "Bob", "password": "bob-secret"})

    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Bob"}


def test_login_refresh_me_logout_success():
    client.post("/auth/register", json={"name": "Bob", "password": "bob-secret"})
    login_response = client.post("/auth/login", json={"name": "Bob", "password": "bob-secret"})

    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me_response.status_code == 200
    assert me_response.json()["name"] == "Bob"

    refresh_response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()

    logout_response = client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout_response.status_code == 200


def test_bruteforce_protection():
    for _ in range(5):
        response = client.post("/auth/login", json={"name": "Alice", "password": "wrong"})
        assert response.status_code == 401

    blocked_response = client.post("/auth/login", json={"name": "Alice", "password": "wrong"})
    assert blocked_response.status_code == 429
