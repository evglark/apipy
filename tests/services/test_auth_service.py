import pytest
from apipy.auth.service import login_user, register_user
from apipy.users.models import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_register_user_creates_record(db_session):
    created_user = await register_user(
        "student", "student@example.com", "password123", db_session
    )

    assert created_user.id is not None
    assert created_user.name == "student"
    assert created_user.email == "student@example.com"


@pytest.mark.asyncio
async def test_login_user_returns_none_for_invalid_password(db_session):
    await register_user("student", "student@example.com", "password123", db_session)

    login_result = await login_user("student@example.com", "wrong", db_session)

    assert login_result is None


@pytest.mark.asyncio
async def test_login_user_returns_tokens_for_valid_credentials(db_session):
    await register_user("student", "student@example.com", "password123", db_session)
    result = await db_session.execute(
        select(User).where(User.email == "student@example.com")
    )
    user = result.scalar_one()
    user.email_verified = True
    await db_session.commit()

    login_result = await login_user(
        "student@example.com", "password123", db_session
    )

    assert login_result is not None
    assert login_result["token_type"] == "bearer"
    assert "access_token" in login_result
    assert "refresh_token" in login_result
    assert "session_id" in login_result
