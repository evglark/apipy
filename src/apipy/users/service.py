def get_all_users(db):
    return db


def get_user_by_id(user_id: int, db):
    for user in db:
        if user["id"] == user_id:
            return user
    return None


def create_user(data: dict, db):
    new_user = {
        "id": len(db) + 1,
        "name": data["name"],
    }
    db.append(new_user)
    return new_user


def update_user(user_id: int, data: dict, db):
    user = get_user_by_id(user_id, db)
    if not user:
        return None

    user["name"] = data["name"]
    return user


def patch_user(user_id: int, data: dict, db):
    user = get_user_by_id(user_id, db)
    if not user:
        return None

    for field, value in data.items():
        user[field] = value
    return user


def delete_user(user_id: int, db):
    for i, user in enumerate(db):
        if user["id"] == user_id:
            return db.pop(i)
    return None
