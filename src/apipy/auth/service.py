from apipy.users.service import create_user, get_all_users


def login_user(name: str, password: str, users_db, credentials_db):
    users = get_all_users(users_db)
    for user in users:
        if user["name"] != name:
            continue

        for credentials in credentials_db:
            if credentials["user_id"] == user["id"] and credentials["password"] == password:
                return {
                    "access_token": f"token-{user['id']}",
                    "token_type": "bearer",
                }
    return None


def register_user(name: str, password: str, users_db, credentials_db):
    users = get_all_users(users_db)
    for user in users:
        if user["name"] == name:
            return None

    created_user = create_user({"name": name}, users_db)
    credentials_db.append({"user_id": created_user["id"], "password": password})
    return created_user
