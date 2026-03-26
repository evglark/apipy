from fastapi.testclient import TestClient
from apipy.main import app

client = TestClient(app)


def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user():
    response = client.post("/users/", json={"name": "Alice"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Alice"
    assert "id" in data


def test_update_user():
    response = client.put("/users/1", json={"name": "Bob"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Bob"}


def test_update_user_returns_404_when_not_found():
    response = client.put("/users/999", json={"name": "Bob"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_patch_user():
    response = client.patch("/users/1", json={"name": "Bob"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Bob"}


def test_patch_user_with_empty_payload():
    response = client.patch("/users/1", json={})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice"}


def test_patch_user_returns_404_when_not_found():
    response = client.patch("/users/999", json={"name": "Bob"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
