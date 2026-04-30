import pytest

from apipy.storage import reset_state_with_seeds


@pytest.fixture(autouse=True)
def reset_state():
    reset_state_with_seeds()
