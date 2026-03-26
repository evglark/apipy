from apipy.services.user_service import (
    get_user_by_id,
    create_user,
    update_user,
    patch_user,
    delete_user,
)


def test_create_user(db):
    user = create_user({"name": "Alice"}, db)

    assert user["id"] == 1
    assert user["name"] == "Alice"
    assert len(db) == 1


def test_get_user_by_id():
    db = [{"id": 1, "name": "Alice"}]
    user = get_user_by_id(1, db)

    assert user["name"] == "Alice"


def test_delete_user():
    db = [{"id": 1, "name": "Alice"}]
    user = delete_user(1, db)

    assert user["id"] == 1
    assert len(db) == 0


def test_update_user():
    db = [{"id": 1, "name": "Alice"}]
    user = update_user(1, {"name": "Bob"}, db)

    assert user == {"id": 1, "name": "Bob"}
    assert db == [{"id": 1, "name": "Bob"}]


def test_update_user_returns_none_when_not_found():
    db = [{"id": 1, "name": "Alice"}]
    user = update_user(2, {"name": "Bob"}, db)

    assert user is None
    assert db == [{"id": 1, "name": "Alice"}]


def test_patch_user():
    db = [{"id": 1, "name": "Alice"}]
    user = patch_user(1, {"name": "Bob"}, db)

    assert user == {"id": 1, "name": "Bob"}
    assert db == [{"id": 1, "name": "Bob"}]


def test_patch_user_with_empty_payload_keeps_user_unchanged():
    db = [{"id": 1, "name": "Alice"}]
    user = patch_user(1, {}, db)

    assert user == {"id": 1, "name": "Alice"}
    assert db == [{"id": 1, "name": "Alice"}]


def test_patch_user_returns_none_when_not_found():
    db = [{"id": 1, "name": "Alice"}]
    user = patch_user(2, {"name": "Bob"}, db)

    assert user is None
    assert db == [{"id": 1, "name": "Alice"}]
