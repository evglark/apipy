from apipy.storage import build_seed_state, reset_state_with_seeds
import apipy.storage as storage


def test_build_seed_state_contains_expected_collections():
    state = build_seed_state()

    assert "users" in state
    assert "credentials" in state
    assert "refresh_tokens" in state
    assert "token_blacklist" in state
    assert "login_attempts" in state
    assert "ip_rate_limit" in state
    assert "security_events" in state
    assert "magic_tokens" in state


def test_reset_state_with_seeds_restores_default_user():
    storage.STATE["users"].clear()
    storage.STATE["users"].append({"id": 99, "name": "Tmp", "email": "tmp@example.com"})

    reset_state_with_seeds()

    assert storage.STATE["users"] == [{"id": 1, "name": "Alice", "email": "alice@example.com"}]
