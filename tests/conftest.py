import pytest
from apipy.routers.users import fake_db


@pytest.fixture
def db():
    return []


@pytest.fixture(autouse=True)
def reset_fake_db():
    fake_db[:] = [{"id": 1, "name": "Alice"}]
