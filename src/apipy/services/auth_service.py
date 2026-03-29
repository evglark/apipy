import hashlib
import secrets
from datetime import datetime, timezone


# --- "БД" авторизации в памяти ---
# Структура записи: {"id": int, "username": str, "password_hash": str, "salt": str}
#
# TODO(postgres+docker): заменить in-memory список на репозиторий PostgreSQL,
# который будет работать через docker-compose сервис postgres.
auth_users_db: list[dict] = []


# --- "Сессии" в памяти ---
# token -> user_id. Нужны только для демонстрации успешной авторизации.
#
# TODO(postgres+docker): вынести сессии в устойчивое хранилище (или Redis),
# а для JWT добавить ротацию ключей и проверку срока жизни.
auth_sessions_db: dict[str, int] = {}


def _hash_password(password: str, salt: str) -> str:
    """Возвращает SHA-256 хэш для пары password+salt.

    Это демонстрационный вариант для обучения. В production нужно использовать
    алгоритмы для паролей: bcrypt / argon2 / scrypt.
    """

    payload = f"{password}:{salt}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _generate_token(user_id: int) -> str:
    """Генерируем простой токен.

    Формат токена специально читаемый, чтобы было понятно на обучении,
    из каких частей он состоит.
    """

    random_part = secrets.token_urlsafe(16)
    issued_at = datetime.now(timezone.utc).timestamp()
    return f"uid-{user_id}.{int(issued_at)}.{random_part}"


def get_auth_user_by_username(username: str, db: list[dict]) -> dict | None:
    """Ищет пользователя авторизации по username."""

    for user in db:
        if user["username"] == username:
            return user
    return None


def register_user(username: str, password: str, db: list[dict]) -> dict:
    """Регистрирует пользователя в in-memory хранилище.

    Возвращает словарь с id и username (без пароля).
    """

    salt = secrets.token_hex(8)
    password_hash = _hash_password(password=password, salt=salt)

    new_user = {
        "id": len(db) + 1,
        "username": username,
        "password_hash": password_hash,
        "salt": salt,
    }
    db.append(new_user)

    return {"id": new_user["id"], "username": new_user["username"]}


def login_user(
    username: str,
    password: str,
    users_db: list[dict],
    sessions_db: dict[str, int],
) -> dict | None:
    """Проверяет пару username/password и создает токен-сессию."""

    auth_user = get_auth_user_by_username(username=username, db=users_db)
    if not auth_user:
        return None

    password_hash = _hash_password(password=password, salt=auth_user["salt"])
    if password_hash != auth_user["password_hash"]:
        return None

    access_token = _generate_token(user_id=auth_user["id"])
    sessions_db[access_token] = auth_user["id"]

    return {"access_token": access_token, "user_id": auth_user["id"]}
