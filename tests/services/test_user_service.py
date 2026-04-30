import pytest
from apipy.users.service import (
    get_user_by_id,
    create_user,
    update_user,
    patch_user,
    delete_user,
)


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = await create_user({"name": "Alice", "email": "alice@test.com"}, db_session)

    assert user.id is not None
    assert user.name == "Alice"


@pytest.mark.asyncio
async def test_get_user_by_id(db_session):
    user_in = await create_user(
        {"name": "Alice", "email": "alice@test.com"}, db_session
    )
    user = await get_user_by_id(user_in.id, db_session)

    assert user.name == "Alice"


@pytest.mark.asyncio
async def test_delete_user(db_session):
    user_in = await create_user(
        {"name": "Alice", "email": "alice@test.com"}, db_session
    )
    user = await delete_user(user_in.id, db_session)

    assert user.id == user_in.id

    check = await get_user_by_id(user_in.id, db_session)
    assert check is None


@pytest.mark.asyncio
async def test_update_user(db_session):
    user_in = await create_user(
        {"name": "Alice", "email": "alice@test.com"}, db_session
    )
    user = await update_user(
        user_in.id, {"name": "Bob", "email": "bob@test.com"}, db_session
    )

    assert user.name == "Bob"
    assert user.email == "bob@test.com"


@pytest.mark.asyncio
async def test_update_user_returns_none_when_not_found(db_session):
    user = await update_user(999, {"name": "Bob", "email": "bob@test.com"}, db_session)
    assert user is None


@pytest.mark.asyncio
async def test_patch_user(db_session):
    user_in = await create_user(
        {"name": "Alice", "email": "alice@test.com"}, db_session
    )
    user = await patch_user(user_in.id, {"name": "Bob"}, db_session)

    assert user.name == "Bob"
    assert user.email == "alice@test.com"


@pytest.mark.asyncio
async def test_patch_user_returns_none_when_not_found(db_session):
    user = await patch_user(999, {"name": "Bob"}, db_session)
    assert user is None
