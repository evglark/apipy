from fastapi.testclient import TestClient

from apipy.main import app

client = TestClient(app)


def test_login_success():
    response = client.post("/auth/login", json={"name": "Alice", "password": "password123"})

    assert response.status_code == 200
    assert response.json() == {"access_token": "token-1", "token_type": "bearer"}


def test_login_invalid_credentials():
    response = client.post("/auth/login", json={"name": "Alice", "password": "bad"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
