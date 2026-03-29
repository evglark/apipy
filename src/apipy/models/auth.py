from pydantic import BaseModel, Field


class AuthRegisterRequest(BaseModel):
    """DTO для регистрации: логин + пароль.

    В учебных целях сохраняем минимально возможный контракт.
    """

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class AuthLoginRequest(BaseModel):
    """DTO для входа: те же поля, что и у регистрации."""

    username: str
    password: str


class AuthResponse(BaseModel):
    """Ответ авторизации: простой учебный "токен" и идентификатор пользователя."""

    access_token: str
    token_type: str = "bearer"
    user_id: int
