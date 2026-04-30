import pytest

from apipy.auth.models import fake_credentials_db
from apipy.users.models import fake_db


@pytest.fixture
def db():
    return []


@pytest.fixture(autouse=True)
def reset_fake_db():
    fake_db[:] = [{"id": 1, "name": "Alice"}]
    fake_credentials_db[:] = [{"user_id": 1, "password": "password123"}]
