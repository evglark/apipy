import pytest
from sqlalchemy import select
from apipy.users.models import User


async def _admin_auth_headers(client, db_session):
    await client.post(
        "/auth/register",
        json={
            "name": "admin",
            "email": "admin@example.com",
            "password": "password123",
            "role": "admin",
        },
    )
    # Manually verify email in the database
    result = await db_session.execute(
        select(User).where(User.email == "admin@example.com")
    )
    user = result.scalar_one()
    user.email_verified = True
    await db_session.commit()

    login = await client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "password123"}
    )
    data = login.json()
    if "access_token" not in data:
        raise Exception(f"Login failed: {data}")
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_users(client, db_session):
    headers = await _admin_auth_headers(client, db_session)
    response = await client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_user(client, db_session):
    headers = await _admin_auth_headers(client, db_session)
    response = await client.post(
        "/users/",
        json={"name": "Alice", "email": "alice2@example.com"},
        headers=headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice2@example.com"
    assert data["role"] == "user"
    assert "id" in data


@pytest.mark.asyncio
async def test_update_user(client, db_session):
    headers = await _admin_auth_headers(client, db_session)
    # First create a user
    create_res = await client.post(
        "/users/", json={"name": "Old", "email": "old@example.com"}, headers=headers
    )
    user_id = create_res.json()["id"]

    response = await client.put(
        f"/users/{user_id}",
        json={"name": "Bob", "email": "bob@example.com"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "name": "Bob",
        "email": "bob@example.com",
        "role": "user",
    }


@pytest.mark.asyncio
async def test_update_user_returns_404_when_not_found(client, db_session):
    headers = await _admin_auth_headers(client, db_session)
    response = await client.put(
        "/users/999", json={"name": "Bob", "email": "bob@example.com"}, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_patch_user(client, db_session):
    headers = await _admin_auth_headers(client, db_session)
    create_res = await client.post(
        "/users/", json={"name": "Alice", "email": "alice@example.com"}, headers=headers
    )
    user_id = create_res.json()["id"]

    response = await client.patch(
        f"/users/{user_id}", json={"name": "Bob"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "name": "Bob",
        "email": "alice@example.com",
        "role": "user",
    }


@pytest.mark.asyncio
async def test_patch_user_returns_404_when_not_found(client, db_session):
    headers = await _admin_auth_headers(client, db_session)
    response = await client.patch("/users/999", json={"name": "Bob"}, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
