from apipy.services.user_service import (
    get_user_by_id,
    create_user,
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
