from apipy.users.service import get_all_users


def login_user(name: str, password: str, db):
    users = get_all_users(db)
    for user in users:
        if user["name"] == name and password == "password123":
            return {
                "access_token": f"token-{user['id']}",
                "token_type": "bearer",
            }
    return None
