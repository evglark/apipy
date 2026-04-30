import pytest


@pytest.mark.asyncio
async def test_get_users(client):
    response = await client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/users/", json={"name": "Alice", "email": "alice2@example.com"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice2@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_update_user(client):
    # First create a user
    create_res = await client.post(
        "/users/", json={"name": "Old", "email": "old@example.com"}
    )
    user_id = create_res.json()["id"]

    response = await client.put(
        f"/users/{user_id}", json={"name": "Bob", "email": "bob@example.com"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": user_id, "name": "Bob", "email": "bob@example.com"}


@pytest.mark.asyncio
async def test_update_user_returns_404_when_not_found(client):
    response = await client.put(
        "/users/999", json={"name": "Bob", "email": "bob@example.com"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_patch_user(client):
    create_res = await client.post(
        "/users/", json={"name": "Alice", "email": "alice@example.com"}
    )
    user_id = create_res.json()["id"]

    response = await client.patch(f"/users/{user_id}", json={"name": "Bob"})
    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "name": "Bob",
        "email": "alice@example.com",
    }


@pytest.mark.asyncio
async def test_patch_user_returns_404_when_not_found(client):
    response = await client.patch("/users/999", json={"name": "Bob"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
