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
