import pytest

from apipy.routers.users import fake_db
from apipy.services.auth_service import auth_sessions_db, auth_users_db


@pytest.fixture
def db():
    return []


@pytest.fixture(autouse=True)
def reset_fake_db():
    fake_db[:] = [{"id": 1, "name": "Alice"}]


@pytest.fixture(autouse=True)
def reset_auth_db():
    auth_users_db.clear()
    auth_sessions_db.clear()
