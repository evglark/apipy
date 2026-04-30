import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post(
        "/auth/register",
        json={
            "name": "student",
            "email": "student@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "student"
    assert payload["email"] == "student@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_returns_400(client):
    await client.post(
        "/auth/register",
        json={
            "name": "student",
            "email": "student@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/auth/register",
        json={
            "name": "student",
            "email": "student@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/auth/register",
        json={
            "name": "student",
            "email": "student@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/auth/login",
        json={"name": "student", "password": "password123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert "access_token" in payload
    assert "refresh_token" in payload
    assert "session_id" in payload


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401(client):
    response = await client.post(
        "/auth/login",
        json={"name": "student", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
