import pytest

from apipy.auth.models import (
    fake_credentials_db,
    ip_rate_limit_db,
    login_attempts_db,
    refresh_tokens_db,
    security_events_db,
    token_blacklist,
)
from apipy.auth.security import hash_password
from apipy.users.models import fake_db


@pytest.fixture
def db():
    return []


@pytest.fixture(autouse=True)
def reset_fake_db():
    fake_db[:] = [{"id": 1, "name": "Alice"}]
    fake_credentials_db[:] = [{"user_id": 1, "password_hash": hash_password("password123")}]
    refresh_tokens_db[:] = []
    token_blacklist.clear()
    login_attempts_db.clear()
    ip_rate_limit_db.clear()
    security_events_db[:] = []
